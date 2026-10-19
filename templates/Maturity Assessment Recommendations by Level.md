# **Maturity Assessment Recommendations**

This document complements the [Maturity Assessment Playbook](https://docs.google.com/document/d/1RorsDqNW8Ad8jzi7SBIz45DNhW3rKC5PSnlEGU6759M/edit?tab=t.0#heading=h.gjdgxs) and gives structure to the recommendations we should add when delivering the [Maturity Assessment Template](https://docs.google.com/document/d/1sTkEWY_dOZlRLFLBvWCvKtnJZRGNj1qVwfS-TTRvfuA/edit?tab=t.0#heading=h.sv7l6fzhs950) to the customer.

# To Achieve Level 2

### Involve Developers directly

SonarQube for IDE provides real-time feedback on code quality, helping developers identify and fix issues as they code, before the commit.  Developers can also connect SonarQube for IDE to SonarQube to synchronise configuration and manage issues from their IDE.

- [ ] Promote SonarQube for IDE adoption

      Many users are not aware of the existence of SonarQube for IDE and the benefits of using Connected Mode.  Fostering awareness through communications and installation assistance can help increase adoption within your developer community. See [SonarQube for IDE Connected Mode](https://docs.sonarsource.com/sonarqube/9.9/user-guide/sonarlint-connected-mode/) documentation.

# To Achieve Level 3

### Integrate with DevOps Platform(s)

Sonar’s products offer additional benefits when integrated with the DevOps platforms you are using. Each repository can be easily onboarded, set up for scanning, and tightly integrated so that you can begin to practice Clean as You Code.

- [ ] Integrate with GitHub

      By connecting your SonarQube instance with GitHub, you can quickly set up Projects and report the Quality Gate status to your Pull Requests. See [GitHub integration](https://docs.sonarsource.com/sonarqube/9.9/devops-platform-integration/github-integration/) documentation.

- [ ] Integrate with Azure DevOps

      By adding the SonarQube extension to Azure DevOps, you can easily add scanning to Azure Pipelines through the SonarQube extension. See [Azure DevOps integration](https://docs.sonarsource.com/sonarqube/9.9/devops-platform-integration/azure-devops-integration/) documentation.

### Automate Code Scanning

To keep code as clean from vulnerabilities as possible, users should expect to receive feedback within twenty-four hours of committing.  This requires that Sonar analysis is run in a timely manner through automation. See the [Configuring branch analysis](https://docs.sonarsource.com/sonarqube/9.9/devops-platform-integration/azure-devops-integration/#configuring-branch-analysis) documentation.

- [ ] Automate Azure Pipeline branch scanning

      Under the Triggers tab of your pipeline, select Enable continuous integration and select all the branches for which you want SonarQube analysis to run automatically.

- [ ] #### Publish Quality Gate results

      Displaying the Quality Gate status in the build summary increases the visibility of your analysis results. You can enable this by adding the **“[Publish Quality Gate Result](https://docs.sonarsource.com/sonarqube-server/2025.1/devops-platform-integration/azure-devops-integration/adding-analysis-to-pipeline/quality-gate-status-in-release-pipeline)”** task to your pipelines.

# To Achieve Level 4

### Validate New Code Settings

Defining what is considered new code is an important part of code quality and security. By focusing on code that's been added or changed since your new code definition, you can set consistent quality requirements and expectations. Your new code will be issue-free and you'll clean up the code you encounter along the way.  See [Defining New Code](https://docs.sonarsource.com/sonarqube/9.9/project-administration/defining-new-code/) documentation.

- [ ] Set default New Code setting

      The default New Code setting will be applied to all new Projects and is set through the global administration options. If your Projects consistently use Project versioning and update it upon release, the “Project Version” setting is the best default option. Otherwise, a “Number of Days” setting that closely matches your sprint/release cycle is a good default.

- [ ] Educate Project Administrators on New Code options

      ### Project administrators should be aware of the additional options for New Code so that they can choose the option that best suits their teams' work. Options may be set at the Project level or on individual branches.

### Enforce Quality Gates

- [ ] Add Branch Protection Rules to GitHub repositories

      The best time to enforce coding standards is during a pull request review.  Using GitHub Branch protection rules, you can block the merging of code when the Sonar Quality Gate fails.  These rules should be set for all main branches on your repositories. See [Github integration](https://docs.sonarsource.com/sonarqube/9.9/devops-platform-integration/github-integration/#preventing-pull-request-merges-when-the-quality-gate-fails) documentation

- [ ] Stop code promotion when Quality Gate is failing

      To prevent the promotion of code with low quality, your organisation should commit to stop promoting code when the Quality Gate is failing.  This requires developers taking personal responsibility for their code by fixing issues as they are detected.  Also, teams and leadership should be aware of and respect the Quality Gate status of their projects.  Once this practice is in place, you can expect to stop the accumulation of technical debt and see a gradual increase in the quality of your overall codebase.

# To Achieve Level 5

- [ ] #### Track SonarQube for IDE usage

      You can track the usage of SonarQube for IDE in Connected Mode through the SonarQube UI and via the Web API. Use this reporting to gauge the success of your promotion efforts.  
      

### Consolidate Quality Standards

When many Quality Profiles and Quality Gates are in place within your organisation, it is impossible to maintain a standard of quality. Quality governance management should be a central function, and updates should benefit the entire developer community, not individual teams.

- [ ] Restrict access to “Administer Quality Profiles/Gates” privilege

      Ensure that your user onboarding process does not grant the “Administer Quality Profile” or “Administer Quality Gates” privilege to most users. Users with the global “Administrator” privilege can remove this privilege from any users who are not designated to make changes for the entire organisation. See the [Global Permissions](https://docs.sonarsource.com/sonarqube/9.9/instance-administration/security/#global-permissions) documentation.

- [ ] Create default Quality Profiles

      Using the “Sonar Way” built-in Quality Profiles as a starting point, develop a default Quality Profile for each language you are analysing that aligns with your expected standard of clean code.  If you expect to need some variation to account for coding patterns used in a few projects, extend the default and modify it so that future changes to the default are incorporated. See [Quality Profile](https://docs.sonarsource.com/sonarqube/9.9/instance-administration/quality-profiles/) documentation.

- [ ] Create a default Quality Gate

      Develop a default Quality Gate that represents the issues you want developers to resolve immediately upon detection. The built-in “Sonar Way” Quality Gate represent’s Sonar’s recommendation for following best practices practices.  This also acts as a great starting point should you choose to customise. See [Quality Gates](https://docs.sonarsource.com/sonarqube/9.9/user-guide/quality-gates/) documentation

- [ ] Remove legacy settings

      Once the new default Quality Profiles and Quality Gates have been established, projects using legacy versions should be moved to the default. Be sure to notify teams that this is happening, as they will see a change in results following the switch. Following this migration, remove the legacy Quality Profiles and Quality Gates.

      

      

