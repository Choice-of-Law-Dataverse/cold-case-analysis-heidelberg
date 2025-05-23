# CoLD Case Analyzer as an Agent

CoLD Case Analyzer as an agent describes the implementation of the case analysis logic within the scope of an AI agent, using the langgraph framework. This endeavor aims to establish an intuitive system, which lets jurists chat with the CoLD Case Analyzer and through this chat not only receive the automated analysis of court decisions immediately but also be able to influence or correct the system.

## Workflow

A typical workflow for the agent would look something like this:

```{mermaid.js}
flowchart TD
    Step1[Text of the Court Decision]:::color2
    Step2[Choice of Law Section<br>- Is this correct? -]:::color1
    Step3.1[Yes]:::color2
    Step3.2[No]:::color2
    Step4[Private International Law Theme<br>- Is this correct? -]:::color1
    Step5.1[Yes]:::color2
    Step5.2[No]:::color2
    Step6[Here is the complete analysis:<br>## Abstract<br>...<br>## Relevant Facts<br>...<br>##PIL Provisions<br>...<br>##Choice of Law Issue<br>...<br>## Court's Position<br>...]:::color1
    Step7.1[User Feedback Good]:::color2
    Step7.2[User Feedback Bad]:::color2
    End:::color3

    Step1 --> Step2
    Step2 --> Step3.1
    Step2 --> Step3.2
    Step3.1 --> Step4
    Step4 --> Step5.1
    Step4 --> Step5.2
    Step5.1 --> Step6
    Step6 --> Step7.1
    Step6 --> Step7.2
    Step7.1 --> End

    %% Feedback loops
    Step3.2 -- "Please include/remove XYZ" --> Step2
    Step5.2 -- "It should be XYZ" --> Step4
    Step7.2 -- "Please improve XYZ" --> Step6

    %% Define alternating styles
    classDef color1 color:black,fill:lightblue,stroke:blue,stroke-width:2px;
    classDef color2 color:black,fill:lightyellow,stroke:orange,stroke-width:2px;
    classDef color3 color:black,fill:lightgreen,stroke:green,stroke-width:2px;
```

There are two first steps, where the model tries to come up with essential details about the court decision to be analysed which are necessary for the following analysis steps to be achieved correctly. These two first steps thus each have their own feedback loop, where the user is tasked to provide confirmation or correction of the answer the model came up with. Once these two analyses are established, the model will then go on to complete the full analysis with all analysis categories. The user can finally request more adjustments to the complete analysis, meaning there is a final feedback loop, which can be iterated as often until the user is satisfied.

## Prompts

```{txt}
You are a jurist and a private international law expert. Your task is to analyze a court decision. In a first step you retrieve the following information:
- Choice of Law Section
- PIL Theme

Your task is to return the following analysis categories:
- Abstract
- Relevant Rules
- ...
```