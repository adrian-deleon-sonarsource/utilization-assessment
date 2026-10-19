"""Customer-independent content for maturity assessments.

Jev only *judges* these candidates against each customer's evidence; code writes
the ones that hold. {C} = customer name, {version} = the SonarQube version Jev
selected from the evidence, {latest} = LATEST_LTA.
"""

LATEST_LTA = "2026.5"  # update when a new LTA ships

DOCS = "https://docs.sonarsource.com/sonarqube-server"

# Recommendations beyond the template and the recommendations md, grouped in
# sections that are added to the Recommendations chapter. Each item still goes
# through the same "applies" / "already done" judgments as the others; an item's
# optional "done" ({question, true, false}) replaces the default org-wide test.
EXTRA_SECTIONS = [
    {
        "section": "Leverage AI Capabilities",
        "intro": "Sonar's AI capabilities help developers fix issues faster and give leadership confidence that AI-generated code meets the same quality and security standards as the rest of the codebase.",
        "items": [
            {"key": "enable_ai_codefix", "level": 2, "title": "Enable AI CodeFix",
             "description": f"AI CodeFix uses a large language model to suggest fixes for issues detected by SonarQube, directly in SonarQube and in SonarQube for IDE. It is available in Enterprise and Data Center editions and can use Sonar's hosted models or your own LLM provider. An Instance Administrator can enable it for all projects or for selected projects. See [Enable AI CodeFix]({DOCS}/instance-administration/ai-features/enable-ai-codefix/) documentation.",
             # Enabled once at the instance level, so "in use" is enough; only a
             # documented "selected projects only" setup counts as partial.
             "done": {"question": "Has the customer already enabled AI CodeFix on their SonarQube instance? It is switched on once by an Instance Administrator; any evidence that developers receive or apply AI CodeFix suggestions (for example usage telemetry) shows it is enabled.",
                      "true": "AI CodeFix is enabled on the instance: the evidence says it was turned on, or shows AI CodeFix suggestions being generated or applied.",
                      "false": "There is no evidence AI CodeFix is enabled, or the evidence says it is limited to only selected projects."}},
            {"key": "adopt_ai_code_assurance", "level": 4, "title": "Adopt AI Code Assurance",
             "description": f"Mark projects that contain AI-generated code and apply a Quality Gate qualified for AI code to them, so AI-assisted changes are held to the right standard before they are merged. AI Code Assurance also lets you report which projects contain AI code and whether they meet that standard. See [AI Code Assurance]({DOCS}/quality-standards-administration/ai-code-assurance/overview/) documentation."},
            {"key": "measure_mcp_ai_usage", "level": 5, "title": "Promote and measure the SonarQube MCP Server",
             "description": "The SonarQube MCP Server lets AI assistants and agents query SonarQube issues and Quality Gate results and help fix them. Publish usage guidance for developers, and track AI-assisted remediation (issues fixed and the remediation effort they represent) through the Web API so you can show leadership how AI capabilities are being used. See the [SonarQube MCP Server](https://docs.sonarsource.com/sonarqube-mcp-server/) documentation."},
        ],
    },
    {
        "section": "Maintain Platform Health",
        "intro": "Keeping the SonarQube platform current and clean keeps analysis results trustworthy, keeps license consumption under control, and gives teams access to the newest capabilities.",
        "items": [
            {"key": "upgrade_latest_lta", "level": 3, "title": "Upgrade to the latest LTA and adopt a regular upgrade cadence",
             "description": f"Upgrade to SonarQube Server {{latest}} LTA to benefit from its new capabilities, such as customizable dashboards for projects and portfolios and architecture analysis. A new LTA is released every six months; planning one upgrade per LTA avoids long, multi-hop upgrades and keeps you on a patched version. See the [Release cycle model]({DOCS}/server-update-and-maintenance/update/release-cycle-model/) and [Determine your update path]({DOCS}/server-update-and-maintenance/update/determine-path/) documentation."},
            {"key": "onboard_new_languages", "level": 3, "title": "Onboard newly supported languages",
             "description": f"Recent releases add analysis for languages and technologies such as PowerShell, SQL and more infrastructure-as-code formats. After upgrading, let development teams know which additional code can now be analyzed and onboard it. See [Supported languages]({DOCS}/analyzing-source-code/languages/overview/) documentation."},
            {"key": "plan_license_capacity", "level": 3, "title": "Plan license capacity ahead of renewal",
             "description": f"When license consumption reaches the entitlement, new analyses are rejected. Monitor lines-of-code growth, combine it with expected onboarding (including newly supported languages), and size the license ahead of the renewal so scanning is never interrupted. See [License management]({DOCS}/instance-administration/license-administration/) documentation."},
        ],
    },
    {
        "section": "Drive Adoption and Awareness",
        "intro": "Getting value from SonarQube depends on developers and team leads knowing how to use it; standard conventions make the data reliable for reporting.",
        "items": [
            {"key": "education_program", "level": 2, "title": "Run a SonarQube education program",
             "description": "Provide short, role-based enablement for developers, team leads and project administrators covering how to read analysis results, the New Code approach, Quality Gates, SonarQube for IDE and portfolios. Recorded sessions, internal documentation and office hours help teams get value from SonarQube without relying on the platform team."},
            {"key": "standardize_project_naming", "level": 5, "title": "Standardize project names and keys",
             "description": f"Adopt a naming and key convention for projects (for example, business unit, application and component) and apply it during onboarding. Consistent names make portfolios, reporting and Web API automation reliable. See [Portfolios]({DOCS}/user-guide/portfolios/) documentation."},
        ],
    },
]

# Executive summary candidates; only statements Jev finds supported are written.
SUMMARY_CANDIDATES = {
    "current_version": "The current technical implementation of Sonar is good. {C} runs a recent release ({version}).",
    "authz": "Administration is centralized with a platform team, and elevated permissions are granted to teams on request.",
    "qg_soft": "There are important improvements to make in Code Quality and Security governance: Quality Gates should be enforced (blocking merges) rather than run as soft failures. Configuration adjustments are recommended so that enforcement is not seen as a burden for developers.",
    "qg_enforced": "Quality Gates are enforced: failing code is blocked from being merged or promoted.",
    "qg_fragmented": "Some teams maintain their own custom Quality Gates and Quality Profiles; consolidating on a shared {C} standard would make governance easier.",
    "ide": "SonarQube for IDE should be used more by developers to detect issues early (shift left) and fix them before committing the code.",
    "portfolios": "Increased use of portfolios would allow better management reporting on overall {C} code quality and security.",
    "license": "License consumption is growing quickly and approaching the current entitlement; capacity should be planned ahead of the renewal.",
    "education": "There is an education and awareness gap among developers and team leads on how to get value from SonarQube.",
    "upgrade_latest": "Upgrading to SonarQube {latest} LTA would give {C} customizable dashboards for projects and portfolios, new languages such as PowerShell, and new AI and agentic capabilities.",
    "mcp": "{C} has enabled the SonarQube MCP Server, and developers already use it with AI assistants to fix issues.",
    "leadership_metrics": "{C} leadership wants metrics showing how teams benefit from SonarQube and how its AI capabilities are being used.",
    "onboarding": "There are more software development projects that should be onboarded on SonarQube.",
}

# "<Customer> Current Environment" statements: heading -> {key: statement}.
# Jev keeps the supported ones; telemetry bullets and choices are added by code.
ENV_CANDIDATES = {
    "Installation": {
        "github": "Integrated with GitHub",
        "gitlab": "Integrated with GitLab",
        "azure_devops": "Integrated with Azure DevOps",
        "bitbucket": "Integrated with Bitbucket",
        "kubernetes": "Deployed on Kubernetes",
        "mcp": "SonarQube MCP Server enabled for use with AI assistants",
        "ai_codefix": "AI CodeFix enabled",
        "multi_hop_upgrade": "The last upgrade required multiple LTA hops",
    },
    "Code Analysis": {
        "ci_automated": "Code analysis is automated in CI pipelines",
        "pr_decoration": "Pull requests are analyzed with results decorated in the DevOps platform",
        "qg_soft": "The Quality Gate runs as a pipeline step configured as a soft failure (it does not block)",
        "qg_blocking": "A failing Quality Gate blocks merges or fails the pipeline",
        "monorepo": "Some repositories are monorepos containing several projects",
    },
    "Governance": {
        "platform_team": "A central platform team administers SonarQube",
        "teams_no_admin": "Teams have no administration rights by default and request them from the platform team",
        "sonar_way_default": "Sonar Way is the default Quality Gate and Quality Profile",
        "custom_gates": "Some teams create their own custom Quality Gates or Quality Profiles",
        "groups": "Groups are configured with users",
        "permission_templates": "Permission templates are configured for some teams",
        "ncd_previous_version": "New code definition defaults to \"Previous version\"",
        "ncd_days": "New code definition defaults to a number of days",
        "ncd_reference_branch": "New code definition defaults to a reference branch",
        "portfolios_light": "Portfolios are configured but lightly used",
        "portfolios_active": "Portfolios are actively used for reporting",
        "leadership_metrics": "Leadership wants metrics on adoption and AI usage",
    },
}

# Single-answer facts selected with a Choice (option -> description). "unknown"
# means the evidence does not say; those are left out of the report.
ENV_CHOICES = {
    "edition": ("Which SonarQube Server edition does the customer run?", {
        "Developer Edition": "SonarQube Server Developer Edition",
        "Enterprise Edition": "SonarQube Server Enterprise Edition (portfolios, multiple DevOps integrations)",
        "Data Center Edition": "SonarQube Server Data Center Edition (high availability cluster)",
        "Community Build": "The free SonarQube Community Build",
        "unknown": "The evidence does not say which edition",
    }),
    "database": ("Which database does the customer's SonarQube Server use?", {
        "PostgreSQL": "PostgreSQL",
        "Microsoft SQL Server": "Microsoft SQL Server",
        "Oracle": "Oracle Database",
        "unknown": "The evidence does not say which database",
    }),
    "authentication": ("How do users authenticate to the customer's SonarQube Server?", {
        "GitHub": "Users log in through GitHub (OAuth)",
        "GitLab": "Users log in through GitLab",
        "SAML": "Users log in through SAML single sign-on (Okta, Entra ID, ...)",
        "LDAP": "Users log in with LDAP / Active Directory credentials",
        "local accounts": "Users have local SonarQube accounts",
        "unknown": "The evidence does not say how users authenticate",
    }),
}

# Statements that contradict each other: only the most likely one is kept.
EXCLUSIVE = [
    {"sum_qg_soft", "sum_qg_enforced"},
    {"env_code_analysis_qg_soft", "env_code_analysis_qg_blocking"},
    {"env_governance_ncd_previous_version", "env_governance_ncd_days", "env_governance_ncd_reference_branch"},
    {"env_governance_portfolios_light", "env_governance_portfolios_active"},
]
