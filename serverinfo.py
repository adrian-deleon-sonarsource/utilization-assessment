"""Read a SonarQube system info or support info JSON export from a customer's folder.

Only a whitelist of facts is kept, so no hostnames, URLs, IDs, user names or
secrets reach Jev. Version, edition, database and login method come straight
from the export and replace Jev's choices for those facts.
"""

import json
from pathlib import Path
from urllib.parse import urlparse

EDITIONS = {"community": "Community Build", "developer": "Developer Edition",
            "enterprise": "Enterprise Edition", "data center": "Data Center Edition"}
DATABASES = ("PostgreSQL", "Microsoft SQL Server", "Oracle")
ALMS = {"github": "GitHub", "gitlab": "GitLab", "bitbucket": "Bitbucket Server / Data Center",
        "bitbucketcloud": "Bitbucket Cloud", "azure": "Azure DevOps", "azure_devops": "Azure DevOps"}
PUBLIC_HOSTS = {"api.github.com", "github.com", "gitlab.com", "bitbucket.org", "api.bitbucket.org", "dev.azure.com"}


def find(folder):
    """The newest *.json in the folder that looks like a SonarQube info export."""
    for f in sorted(Path(folder).glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True):
        try:
            data = json.loads(f.read_text())
        except (ValueError, UnicodeDecodeError):
            continue
        if isinstance(data, dict) and isinstance(data.get("System"), dict):
            return f, data
    return None, None


def load(folder):
    """Return (export file name or None, facts dict for Jev, {choice key: value})."""
    f, d = find(folder)
    if not d:
        return None, {}, {}
    system, settings, stats = d["System"], d.get("Settings", {}), d.get("statistics", {})
    on = lambda k: str(settings.get(k, "")).lower() == "true"
    nodes = [n for n in d.get("Application Nodes") or [] if isinstance(n.get("System"), dict)]

    version = system.get("Version") or next((n["System"].get("Version") for n in nodes if n["System"].get("Version")), None)
    version = ".".join(version.split(".")[:3]) if version else None  # drop the build number
    edition = next((v for k, v in EDITIONS.items() if k in str(system.get("Edition", "")).lower()), None)
    db = d.get("Database", {})
    database = next((x for x in DATABASES if x.lower() in str(db.get("Database", "")).lower()), None)

    auth = [name for key, name in (("saml", "SAML"), ("github", "GitHub"), ("gitlab", "GitLab"), ("bitbucket", "Bitbucket"))
            if on(f"sonar.auth.{key}.enabled")]
    if settings.get("sonar.security.realm") == "LDAP" or "ldap.url" in settings:
        auth.append("LDAP")
    if on("sonar.web.sso.enable"):
        auth.append("HTTP header SSO")

    facts = {
        "source": "support info export" if "statistics" in d else "system info export",
        "exported": (d.get("Creation Date") or "")[:10] or None,
        "health": d.get("Health"),
        "version": version,
        "edition": system.get("Edition"),
        "lines_of_code": system.get("Lines of Code"),
        "high_availability": system.get("High Availability"),
        "application_nodes": len(nodes) or None,
        "runs_in_containers": system.get("Container"),
        "kubernetes": on("sonar.cluster.kubernetes") if "sonar.cluster.kubernetes" in settings else None,
        "database": " ".join(x for x in (db.get("Database"), db.get("Database Version")) if x) or None,
        "authentication": auth or ["local accounts"],
        "force_authentication": system.get("Force authentication"),
        "github_groups_sync": on("sonar.auth.github.groupsSync") if "sonar.auth.github.groupsSync" in settings else None,
        "devops_integrations": _alms(d.get("ALMs") or {}) or None,
        "default_new_code_definition": settings.get("Default New Code Definition"),
        "default_project_visibility": settings.get("projects.default.visibility"),
        "mqr_mode": on("sonar.multi-quality-mode.enabled") if "sonar.multi-quality-mode.enabled" in settings else None,
        "mcp_server_enabled": (d.get("MCP") or {}).get("Enabled", on("sonar.mcp.enabled") if "sonar.mcp.enabled" in settings else None),
        "ai_codefix": "hidden" if on("sonar.ai.codefix.hidden") else settings.get("sonar.ai.suggestions.enabled"),
        "ai_code_autodetect": on("sonar.autodetect.ai.code") if "sonar.autodetect.ai.code" in settings else None,
        "sca_enabled": on("sonar.sca.featureEnabled") if "sonar.sca.featureEnabled" in settings else None,
        "governance_reports": {k.split(".")[-2]: v for k, v in settings.items() if k.startswith("sonar.governance.report.") and k.endswith(".frequency")} or None,
        "jira_integration": "sonar.jira.url" in settings or None,
        "third_party_plugins": [str(v).split("[")[-1].rstrip("]") for v in (d.get("Plugins") or {}).values()] or None,
        "ide_connected_clients": (d.get("Server Push Connections") or {}).get("SonarLint Connected Clients"),
        "compute_engine": _ce(d.get("Compute Engine Tasks") or {}),
    }
    if lic := d.get("License"):
        facts["license"] = {"max_loc": lic.get("maxLoc"), "expires": lic.get("expiresAt"), "type": lic.get("type")}
    if stats:
        since = (stats.get("analysesCountStartDate") or "")[:10]
        langs = sorted(stats.get("nclocByLanguage") or [], key=lambda x: -x.get("ncloc", 0))[:10]
        facts.update({
            "installed": (stats.get("installationDate") or "")[:10] or None,
            "users": stats.get("userCount"),
            "users_logged_in_last_30_days": stats.get("last30DaysLoggedInUserCount"),
            "ide_weekly_users": stats.get("sonarlintWeeklyUsers"),
            "projects": stats.get("projectCount"),
            "projects_not_analyzed": stats.get("projectNotAnalyzedCount"),
            f"branch_analyses_since_{since}": _int(stats.get("branchAnalysesCount")),
            f"pr_analyses_since_{since}": _int(stats.get("prAnalysesCount")),
            "issues_by_status": stats.get("issueCountsByStatus"),
            "top_languages_by_loc": {x["language"]: x["ncloc"] for x in langs} or None,
        })

    choices = {"version": version, "edition": edition, "database": database, "authentication": " and ".join(auth) if auth else None}
    return f.name, {k: v for k, v in facts.items() if v is not None}, {k: v for k, v in choices.items() if v}


def _alms(alms):
    """'Alm:github, Url:https://api.github.com, ...' -> 'GitHub (cloud)' / '... (self-hosted)'."""
    out = []
    for value in alms.values():
        parts = dict(p.split(":", 1) for p in str(value).split(", ") if ":" in p)
        name = ALMS.get(parts.get("Alm", "").strip().lower(), parts.get("Alm", "").strip())
        host = urlparse(parts.get("Url", "").strip()).hostname or ""
        if name:
            out.append(f"{name} ({'cloud' if host in PUBLIC_HOSTS else 'self-hosted'})" if host else name)
    return sorted(set(out))


def _ce(ce):
    keys = {"workers": ("Worker Count", "Max Workers per Node"), "pending": ("Pending", "Total Pending"),
            "failed_tasks": ("Processed With Error",), "succeeded_tasks": ("Processed With Success",)}
    out = {k: next((ce[n] for n in names if n in ce), None) for k, names in keys.items()}
    return {k: v for k, v in out.items() if v is not None} or None


def _int(s):
    try:
        return int(s)
    except (TypeError, ValueError):
        return None
