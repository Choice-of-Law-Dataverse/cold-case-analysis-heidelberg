"""
court_decision_analyzer.py
=========================

A script to build and test a Court Decision Analyzer agent that:
- Analyzes and summarizes court decisions using specialized tools
- Allows for interactive feedback and improvements
- Maintains context of previous iterations
- Provides structured, clear summaries
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import Tool
from pydantic import BaseModel, Field

# Import analysis functions and prompt loader from the case_analyzer module
from case_analyzer import (
    extract_col_section,
    extract_abstract,
    extract_relevant_facts,
    extract_rules_of_law,
    extract_choice_of_law_issue,
    extract_courts_position,
    load_prompt,
)

# 1. Load environment
load_dotenv()

# 2. Initialize the model
# Ensure OPENAI_API_KEY is set in your environment or .env file
model = init_chat_model("gpt-4o-mini", model_provider="openai")

# Placeholder for concepts - replace with actual concepts if available
concepts = []

# 3. Define Tool Input Schemas
class ExtractColSectionInput(BaseModel):
    text: str = Field(description="The full text of the court decision.")

class ExtractAbstractInput(BaseModel):
    text: str = Field(description="The full text of the court decision.")
    col_section: str = Field(description="The previously extracted Choice of Law section.")

class ExtractRelevantFactsInput(BaseModel):
    text: str = Field(description="The full text of the court decision.")
    col_section: str = Field(description="The previously extracted Choice of Law section.")

class ExtractRulesOfLawInput(BaseModel):
    text: str = Field(description="The full text of the court decision.")
    col_section: str = Field(description="The previously extracted Choice of Law section.")

class ExtractChoiceOfLawIssueInput(BaseModel):
    text: str = Field(description="The full text of the court decision.")
    col_section: str = Field(description="The previously extracted Choice of Law section.")

class ExtractCourtsPositionInput(BaseModel):
    text: str = Field(description="The full text of the court decision.")
    col_section: str = Field(description="The previously extracted Choice of Law section.")
    coli: str = Field(description="The previously extracted Choice of Law Issue.")


# 4. Define Tool Functions (Wrappers)
def run_extract_col_section(text: str) -> str:
    """Extracts the Choice of Law section from the court decision text."""
    prompt = load_prompt("col_section.txt")
    return extract_col_section(text, prompt, model)

def run_extract_abstract(text: str, col_section: str) -> str:
    """Extracts the abstract from the court decision text, focusing on the Choice of Law section."""
    prompt = load_prompt("abstract.txt")
    return extract_abstract(text, col_section, prompt, model)

def run_extract_relevant_facts(text: str, col_section: str) -> str:
    """Extracts relevant facts from the court decision text, focusing on the Choice of Law section."""
    prompt = load_prompt("facts.txt")
    return extract_relevant_facts(text, col_section, prompt, model)

def run_extract_rules_of_law(text: str, col_section: str) -> str:
    """Extracts Private International Law provisions/rules from the court decision text, focusing on the Choice of Law section."""
    prompt = load_prompt("rules.txt")
    return extract_rules_of_law(text, col_section, prompt, model)

def run_extract_choice_of_law_issue(text: str, col_section: str) -> dict:
    """Extracts the Choice of Law Issue and classifies its theme from the court decision text, focusing on the Choice of Law section."""
    classification_prompt = load_prompt("issue_classification.txt")
    issue_prompt = load_prompt("issue.txt")
    classification, choice_of_law_issue = extract_choice_of_law_issue(
        text, col_section, classification_prompt, issue_prompt, model, concepts
    )
    # Return both classification (theme) and the issue itself
    return {"theme": classification, "issue": choice_of_law_issue}

def run_extract_courts_position(text: str, col_section: str, coli: str) -> str:
    """Extracts the Court's Position on the Choice of Law Issue from the court decision text."""
    prompt = load_prompt("position.txt")
    return extract_courts_position(text, col_section, prompt, coli, model)


# 5. Create Langchain Tools
tools = [
    Tool(
        name="ExtractChoiceOfLawSection",
        func=run_extract_col_section,
        description="Extracts the relevant Choice of Law (Private International Law) section from the full text of a court decision. This should usually be the first step.",
        args_schema=ExtractColSectionInput,
    ),
    Tool(
        name="ExtractAbstract",
        func=run_extract_abstract,
        description="Creates a concise abstract summarizing the key aspects of the court decision, based on the full text and the extracted Choice of Law section.",
        args_schema=ExtractAbstractInput,
    ),
    Tool(
        name="ExtractRelevantFacts",
        func=run_extract_relevant_facts,
        description="Extracts the relevant facts pertinent to the Choice of Law issue from the court decision, based on the full text and the extracted Choice of Law section.",
        args_schema=ExtractRelevantFactsInput,
    ),
    Tool(
        name="ExtractRulesOfLaw",
        func=run_extract_rules_of_law,
        description="Identifies and extracts the specific Private International Law provisions or legal rules applied or discussed in the Choice of Law section of the court decision.",
        args_schema=ExtractRulesOfLawInput,
    ),
    Tool(
        name="ExtractChoiceOfLawIssueAndTheme",
        func=run_extract_choice_of_law_issue,
        description="Determines the central Choice of Law issue presented in the case and classifies its primary theme, based on the full text and the extracted Choice of Law section. Returns both the theme and the issue.",
        args_schema=ExtractChoiceOfLawIssueInput,
    ),
    Tool(
        name="ExtractCourtsPosition",
        func=run_extract_courts_position,
        description="Extracts the court's final position, reasoning, or holding specifically regarding the identified Choice of Law Issue, based on the full text, the Choice of Law section, and the Choice of Law Issue.",
        args_schema=ExtractCourtsPositionInput,
    ),
]


# 6. Update Agent Instructions
system_instructions = f"""
You are a Court Decision Analyser. Your role is to analyse court decisions focusing on Private International Law (Choice of Law) aspects and provide clear, structured summaries.

You have access to the following tools:
{[tool.name for tool in tools]}

Use these tools to gather the necessary information. Follow this workflow:
1.  Receive the full text of the court decision.
2.  Use `ExtractChoiceOfLawSection` to identify the relevant section(s) discussing Choice of Law.
3.  Use `ExtractChoiceOfLawIssueAndTheme` on the full text and the extracted section to find the core issue and its theme. Store the results (theme and issue).
4.  Use the other extraction tools (`ExtractAbstract`, `ExtractRelevantFacts`, `ExtractRulesOfLaw`, `ExtractCourtsPosition`) using the full text, the extracted Choice of Law section, and the identified Choice of Law Issue (for `ExtractCourtsPosition`) as needed.
5.  Synthesize the results from the tools into a final, structured response with the following sections:
    - Abstract
    - Choice of Law Section (Quote the extracted section)
    - Relevant Facts
    - Private International Law Provisions
    - Private International Law Theme (from ExtractChoiceOfLawIssueAndTheme)
    - Choice of Law Issue (from ExtractChoiceOfLawIssueAndTheme)
    - Court's Position

When receiving feedback:
1) Acknowledge the feedback.
2) Explain your changes, potentially by re-running specific tools or refining the synthesis.
3) Maintain legal accuracy.
4) Keep the summary concise and clear.
"""

# 7. Create the agent executor with tools
memory = MemorySaver()
agent_executor = create_react_agent(
    model,
    tools=tools, # Pass the tools here
    checkpointer=memory
    #messages_modifier=system_instructions # Use messages_modifier for system prompt with ReAct agent
)

# 8. Define analysis and improvement functions (remain largely the same)
def analyse_court_decision(decision_text, thread_id="court-analysis-001"):
    """
    Analyse a court decision using the agent and its tools.

    Args:
        decision_text (str): The text of the court decision
        thread_id (str): Unique identifier for the conversation thread

    Returns:
        dict: Response containing the analysis from the agent's final message
    """
    # Ensure the thread starts clean or retrieve existing state if needed
    config = {"configurable": {"thread_id": thread_id}}
    response = agent_executor.invoke(
        {"messages": [HumanMessage(content=decision_text)]},
        config=config
    )
    # The final answer is usually in the last AIMessage
    return response

def improve_summary(feedback, thread_id="court-analysis-001"):
    """
    Improve the summary based on user feedback using the agent.

    Args:
        feedback (str): User's feedback on the previous summary
        thread_id (str): Unique identifier for the conversation thread

    Returns:
        dict: Response containing the improved analysis from the agent's final message
    """
    config = {"configurable": {"thread_id": thread_id}}
    # The agent receives the feedback as a new HumanMessage in the existing thread
    response = agent_executor.invoke(
        {"messages": [HumanMessage(content=feedback)]},
        config=config
    )
    return response

# Example usage
if __name__ == "__main__":
    # Example court decision text (simplified, focusing on structure)
    # NOTE: This sample text is very basic and might not contain explicit
    #       sections for all the tools to extract perfectly.
    #       A real court decision text is needed for proper testing.
    #sample_decision = input(
    #    "Please enter the full text of the court decision for analysis:\n"
    #)
    sample_decision = """
        Urteilskopf

        136 III 392


        58. Extrait de l'arrêt de la Ire Cour de droit civil dans la cause X. SA contre A. (recours en matière civile)
        4A_91/2010 du 29 juin 2010

        Regeste

        Arbeitsvertrag; unmittelbar anwendbares Recht eines Drittstaates (Art. 19 IPRG).
        Voraussetzungen gemäss Art. 19 IPRG für die Berücksichtigung einer Norm ausländischen Rechts trotz einer Rechtswahl zugunsten schweizerischen Rechts (E. 2.2).
        Zwingende Bestimmung panamaischen Rechts, die einem Matrosen, der auf einem unter panamaischer Flagge fahrenden Schiff beschäftigt ist, eine Entschädigung bei Entlassung einräumt (E. 2.3.1). Enger Zusammenhang zwischen dem Sachverhalt und dem zwingenden Recht des Drittstaates? Frage offengelassen (E. 2.3.2). Der schweizerische Richter kann die panamaische Norm nicht ausnahmsweise berücksichtigen, da nach schweizerischer Rechtsauffassung das Arbeitnehmerinteresse an einer vorgenannten Abgangsentschädigung nicht für schützenswert und überwiegend zu halten ist (E. 2.3.3).

        Sachverhalt ab Seite 393

        BGE 136 III 392 S. 393

        A. Ressortissant espagnol actuellement domicilié en Espagne, A. a travaillé comme soudeur dès le 20 septembre 1989 pour la société de droit suisse Y. SA, à (...), active dans la construction de pipelines sous-marins. Un contrat de travail a été signé par les parties en date du 1er janvier 1996. Dès le 1er mai 2000, les rapports de travail ont été repris tels quels par la société de droit suisse X. SA, à (...), dont le but est la mise à disposition de personnel pour les sociétés du groupe Y. A. travaillait sur le navire ""MV Z."" appartenant au groupe Y. et battant pavillon panaméen.
        Le 23 décembre 2004, X. SA a résilié le contrat de travail pour le 31 mars 2005.

        B. Le 26 avril 2006, A. a déposé une demande contre X. SA devant le Tribunal civil de la Veveyse. Il concluait au paiement d'un montant équivalent à six mois de salaire, soit 31'045,50 euros ou 50'240 fr., plus intérêts. Le demandeur invoquait la loi panaméenne n° 8 du 26 février 1998 sur le travail en mer et sur les voies navigables (ci-après: la loi panaméenne n° 8), décrétée d'ordre public, dont l'art. 56 al. 1 let. f accorde à l'employé qui a travaillé plus de 60 mois sur un bateau une indemnité de licenciement correspondant à 600 % de son salaire mensuel. Il faisait valoir que cette règle de droit panaméen pouvait être prise en considération en application de l'art. 19 LDIP, dès lors que la protection des travailleurs ayant oeuvré longtemps pour le même employeur faisait également partie de l'acquis du droit suisse.
        X. SA a conclu à l'irrecevabilité de la demande, subsidiairement à son rejet.
        Par jugement incident du 31 octobre 2007, le Tribunal civil de la Veveyse a déclaré la demande recevable. Par jugement du 7 novembre 2008, il a rejeté l'action, considérant que seul le droit suisse était applicable, à l'exclusion du droit panaméen.
        Statuant le 16 novembre 2009 sur appel de A., la Ie Cour d'appel civil du Tribunal cantonal du canton de Fribourg a admis le recours
        BGE 136 III 392 S. 394
        et condamné X. SA à verser au travailleur une indemnité de 50'240 fr., plus intérêts à 5 % l'an à partir du 31 mars 2005. L'autorité cantonale a relevé que la loi panaméenne n° 8 avait pour but la protection des travailleurs et que le droit suisse connaissait également des règles de protection, en particulier après de longs rapports de travail ainsi que par le biais de la LAVS et de la LPP. Après avoir constaté qu'aucun système de prévoyance sociale n'avait été appliqué au demandeur, la cour cantonale a jugé, en application de l'art. 19 LDIP, qu'un intérêt légitime et manifestement prépondérant imposait la prise en considération du droit panaméen.

        C. X. SA a interjeté un recours en matière civile. (...) Le Tribunal fédéral a admis le recours, annulé l'arrêt cantonal et rejeté l'action introduite par A. contre X. SA.
        (extrait)

        Erwägungen

        Extrait des considérants:

        2.

        2.1 La recourante reproche tout d'abord à la cour cantonale d'avoir violé l'art. 19 LDIP (RS 291) en prenant en considération l'art. 56 al. 1 let. f de la loi panaméenne n° 8. A son sens, au moins deux des trois conditions cumulatives mises à l'application de la disposition de droit international privé suisse ne sont pas remplies. Premièrement, il ne serait pas établi que la situation en cause ait un lien étroit avec le droit panaméen, l'autorité cantonale relevant elle-même que le rattachement administratif du navire au Panama est le seul lien avec cet Etat. En second lieu, la recourante fait valoir qu'aucun intérêt légitime et manifestement prépondérant au regard de la conception suisse du droit ne justifie l'application du droit panaméen plutôt que du droit suisse, l'art. 339b CO instituant déjà une indemnité à raison de longs rapports de travail qui reste d'actualité pour les travailleurs non soumis à la prévoyance professionnelle obligatoire.
        A titre subsidiaire, la recourante invoque l'arbitraire dans l'établissement des faits. A son avis, les juges fribourgeois ne pouvaient pas déduire de l'absence de déductions sociales sur la fiche de salaire de l'intimé que ce dernier n'était soumis à aucun système de prévoyance. En particulier, la cour cantonale aurait méconnu le principe selon lequel la sécurité sociale est une affaire de souveraineté nationale et qu'elle s'applique aux personnes domiciliées dans le pays concerné, voire aux citoyens de cet Etat travaillant à l'étranger; la recourante se réfère à cet égard au droit espagnol de la sécurité sociale, qui prévoit que les
        BGE 136 III 392 S. 395
        marins émigrants et leur famille de nationalité espagnole peuvent souscrire à une convention spéciale dans ce domaine. En outre, la recourante fait observer que le travailleur n'a jamais allégué qu'il ne bénéficiait d'aucune prévoyance professionnelle, de sorte que la cour cantonale aurait retenu ce fait en violation de l'art. 8 CC.

        2.2 Les parties ont soumis le contrat de travail au droit suisse, qui correspond au droit de l'Etat dans lequel l'employeur a son siège. Ce choix porte sur l'un des droits admis par l'art. 121 al. 3 LDIP (cf. art. 21 al. 4 LDIP). L'élection de droit est par conséquent valable.
        L'art. 19 LDIP relatif aux lois d'application immédiate d'un Etat tiers permet, à certaines conditions, d'écarter le droit choisi par les parties, en particulier dans le domaine du droit du travail (STREIFF/VON KAENEL, Arbeitsvertrag, 6e éd. 2006, n° 24 ad art. 319 CO p. 100 s.; BERNARD DUTOIT, Droit international privé suisse, Commentaire de la loi fédérale du 18 décembre 1987, 4e éd. 2005, n° 8 ad art. 19 LDIP p. 81; FRANK VISCHER, in Zürcher Kommentar zum IPRG, 2e éd. 2004, n° 33 ad art. 19 LDIP; KELLER/KREN KOSTKIEWICZ, in Zürcher Kommentar zum IPRG, 2e éd. 2004, n° 42 et n° 53 ad art. 121 LDIP; STEPHANIE MILLAUER , Sonderanknüpfung fremder zwingender Normen im Bereich von Schuldverträgen [Art. 19 IPRG und Art. 7 Abs. 1 EVÜ], 2001, p. 143; VISCHER/HUBER/OSER, Internationales Vertragsrecht, 2e éd. 2000, n° 906 p. 418). Selon l'alinéa 1 de cette disposition, le juge peut prendre en considération une norme impérative d'un droit autre que celui désigné par la LDIP lorsque des intérêts légitimes et manifestement prépondérants au regard de la conception suisse du droit l'exigent et que la situation visée présente un lien étroit avec ce droit étranger. L'art. 19 al. 2 LDIP précise qu'une prise en considération de la disposition étrangère suppose de tenir compte du but qu'elle vise et des conséquences qu'aurait son application pour arriver à une décision adéquate au regard de la conception suisse du droit. Selon la jurisprudence, le recours à l'art. 19 LDIP doit rester exceptionnel, comme dans tous les cas où une loi d'application immédiate est en jeu (ATF 130 III 620 consid. 3.5.1 s. p. 630 s.; arrêt 5C.60/2004 du 8 avril 2005 consid. 3.1.2, non publié in ATF 131 III 418; cf. DUTOIT, op. cit., n° 4 ad art. 19 LDIP p. 78).

        2.3 Il convient d'examiner si les conditions de l'art. 19 LDIP sont réalisées en l'espèce, comme la cour cantonale l'a admis.

        2.3.1 La première condition a trait à la volonté du législateur étranger d'appliquer la disposition considérée de manière impérative, soit expressément, soit implicitement, en raison du but particulier de la norme (MÄCHLER-ERNE/WOLF-METTIER, in Basler Kommentar, Internationales Privatrecht, 2e éd. 2007, n° 14 ad art. 19 LDIP; DUTOIT, op. cit., n° 4 ad art. 19 LDIP p. 78; VISCHER, op. cit., n° 19 ad art. 19 LDIP).
        En l'espèce, l'autorité cantonale a constaté de manière à lier la cour de céans (cf. ATF 130 III 620 consid. 3.2 p. 625) que, selon son art. 1, la loi panaméenne n° 8 est d'ordre public et règle dans leur totalité les relations entre employeurs et employés à bord des navires battant pavillon panaméen. Il faut en déduire le caractère impératif de l'art. 56 de la loi panaméenne n° 8, qui accorde une indemnité spéciale, variant en principe selon la durée des rapports de travail, au membre d'équipage engagé pour une durée indéterminée et licencié sans juste motif.

        2.3.2 Une autre condition d'application de l'art. 19 LDIP porte sur le lien étroit devant exister entre la situation visée et le droit impératif de l'Etat tiers. L'exigence d'un tel lien suppose plus que n'importe quel rattachement invoqué par la norme étrangère (JEAN-LUC CHENAUX, L'application par le juge des dispositions impératives étrangères non désignées par la règle de conflit du for, in RDS 1988 p. 69). Le juge examinera, du point de vue de l'Etat du for, si les liens de la cause avec le droit de l'Etat tiers sont suffisamment importants pour justifier la prise en considération de la norme impérative étrangère. Un point de rattachement spécial peut consister, notamment, dans le lieu d'exécution, le lieu d'exploitation, le lieu de situation d'une chose ou le lieu de résidence d'une partie au contrat. Il s'agira alors de déterminer si ce rattachement fonde un lien étroit en tenant compte du but et de la fonction de la norme d'intervention de l'Etat tiers (ATF 130 III 620 consid. 3.3.1 p. 625 et les références). Ainsi, par exemple, le lieu de situation de l'objet loué est le critère de rattachement déterminant pour les mesures de protection des locataires (VISCHER, op. cit., n° 21 ad art. 19 LDIP).
        En l'espèce, l'art. 56 de la loi panaméenne n° 8 entend s'appliquer au personnel travaillant sur les navires battant pavillon panaméen. Pour le rattachement objectif, il est admis de manière générale que les rapports de travail des marins sont soumis au droit du pavillon (DUTOIT, op. cit., n° 4 ad art. 121 LDIP p. 422; KELLER/KREN KOSTKIEWICZ, op. cit., n° 31 ad art. 121 LDIP; KURT SIEHR, Das Internationale Privatrecht der Schweiz, 2002, p. 295; le même, Billige Flaggen in teuren Häfen, in Festschrift für Frank Vischer, 1983, p. 314; ROGER HISCHIER, Das Statut des Arbeitsverhältnisses entsandter Arbeitnehmer schweizerischer Unternehmen, 1995, p. 51; SCHÖNENBERGER/JÄGGI, Zürcher Kommentar, 3e éd. 1973, n° 284 ad allgemeine Einleitung). Cette règle se retrouve d'ailleurs dans la loi fédérale du 23 septembre 1953 sur la navigation maritime sous pavillon suisse (LNM; RS 747.30), dont l'art. 68 soumet au droit suisse le contrat d'engagement de tous les marins, quelle que soit leur nationalité, qui servent à bord des navires enregistrés dans le registre des navires suisses et arborant ainsi le pavillon suisse. D'aucuns se sont toutefois interrogés sur le caractère judicieux de ce rattachement pour les travailleurs occupés sur des bâtiments navigant sous un pavillon de complaisance (REITHMANN/MARTINY, Internationales Vertragsrecht, 7e éd. 2010, n° 4870 p. 1447; SIEHR, Billige Flaggen, op. cit., p. 314).
        Dès lors que le pavillon est un rattachement objectif généralement admis en matière de contrat de travail et que le droit suisse applique ce principe aux marins oeuvrant sur les navires arborant le pavillon suisse, il paraît a priori difficile de nier en l'espèce le lien étroit au sens de l'art. 19 LDIP entre les relations de travail des marins et le droit du Panama. D'un autre côté, le pavillon de cet Etat est considéré comme un pavillon de complaisance et la cour cantonale relève elle-même que la seule relation avec le Panama est le rattachement administratif du navire à cet Etat. Or, il s'agit d'une situation dans laquelle il n'existe précisément pas de véritable lien avec l'Etat du pavillon (cf. KELLER/KREN KOSTKIEWICZ, op. cit., n° 32 ad art. 121 LDIP). La question peut toutefois rester ouverte puisque, comme on va le voir, la troisième condition de l'art. 19 LDIP n'est de toute manière pas remplie dans le cas particulier.

        2.3.3 Il y a lieu d'examiner à présent si des intérêts légitimes et manifestement prépondérants au regard de la conception suisse du droit exigent la prise en considération de la norme impérative de l'Etat tiers.

        2.3.3.1 Contrairement à la version française de l'art. 19 LDIP, les versions allemande et italienne précisent que les intérêts en question sont ceux d'une partie. La jurisprudence n'a pas tranché entre les différentes versions (cf. ATF 130 III 620 consid. 3.4.1 p. 628). Il n'est pas nécessaire non plus d'approfondir cette question en l'occurrence. En effet, le texte français, qui a une portée plus large (même arrêt, ibid.), n'exclut pas de prendre en considération les intérêts d'une partie. Or, les intérêts en jeu dans le cas particulier sont manifestement ceux d'une partie, soit le travailleur.

        La mise en oeuvre de l'art. 19 LDIP suppose un jugement de valeur: l'intérêt à l'application de la norme impérative étrangère doit être digne de protection selon la conception suisse du droit et l'emporter manifestement sur l'intérêt à l'application de la lex causae. Conformément à l'art. 19 al. 2 LDIP, l'éventuelle prise en considération du droit impératif d'un Etat tiers dépendra du but poursuivi par la disposition en cause et des conséquences de ce rattachement spécial. L'appréciation se fera selon les valeurs fondamentales de l'ordre juridique suisse. A cet égard, il n'est pas nécessaire que le droit suisse connaisse des normes impératives semblables; il suffit que le but poursuivi par la disposition étrangère soit conforme à la conception suisse (IVO SCHWANDER, Einführung in das internationale Privatrecht, Allgemeiner Teil, 3e éd. 2000, p. 253). L'éventuelle prise en considération de normes d'un Etat tiers doit permettre, dans un cas particulier, d'aboutir à un résultat qui tienne compte de l'effet desdites dispositions sur le rapport juridique en cause et sur la situation de la partie concernée d'une manière conforme à la conception suisse du droit (ATF 130 III 620 consid. 3.5.1 p. 630).
        Dans le domaine du contrat de travail, des dispositions protectrices impératives d'un Etat tiers, en particulier du pays du lieu de travail, pourront trouver à s'appliquer par le biais de l'art. 19 LDIP (VISCHER/HUBER/OSER, op. cit., n° 800 p. 368; ANDREAS BUCHER, Droit international privé suisse, Partie générale, vol. II, 1995, n° 552 p. 217; Message du 10 novembre 1982 concernant une loi fédérale sur le droit international privé, FF 1983 I 403 ch. 282.26). Il s'agira par exemple de normes impératives - de droit public ou de droit privé - relatives au travail le dimanche et les jours fériés, à la durée maximale du travail, à l'interdiction du travail des enfants, à la prévention des risques et des accidents ou encore au salaire minimal (KELLER/KREN KOSTKIEWICZ, op. cit., nos 55-57 ad art. 121 LDIP).

        2.3.3.2 L'art. 56 al. 1 de la loi panaméenne n° 8 accorde au marin licencié sans juste motif une indemnité fixée selon l'échelle suivante:
        let. a: 20 % du salaire mensuel pour une durée de service de 1 à 5 mois;
        let. b: 30 % du salaire mensuel pour une durée de service de plus de 5 mois jusqu'à 11 mois;
        let. c: 100 % du salaire mensuel pour une durée de service de plus de 11 mois jusqu'à 23 mois;
        let. d: 300 % du salaire mensuel pour une durée de service de plus de 23 mois jusqu'à 35 mois;
        BGE 136 III 392 S. 399
        let. e: 400 % du salaire mensuel pour une durée de service de plus de 35 mois jusqu'à 60 mois;
        let. f: 600 % du salaire mensuel pour une durée de service de plus de 60 mois.
        Il ne s'agit pas d'une indemnité pour résiliation immédiate injustifiée au sens où l'entend l'art. 337c CO. En effet, l'indemnité panaméenne est versée dans tous les cas où le contrat de travail de durée indéterminée est résilié, pour autant qu'aucun juste motif ne soit réalisé. L'indemnité en jeu est une indemnité de départ, dont l'ampleur dépend uniquement de la durée des rapports de travail; son montant croît jusqu'à une durée de service de cinq ans, pour ensuite se stabiliser à six mois de salaire mensuel. Elle n'est pas une prime de fidélité à proprement parler puisqu'elle est due déjà après un mois de service, mais la fidélité, jusqu'à cinq ans, est prise en compte dans le calcul du montant dû. L'octroi de l'indemnité panaméenne ne suppose pas que le travailleur licencié ait atteint un certain âge, ni qu'il ait été longtemps au service de l'employeur. Elle se distingue en cela de l'indemnité à raison de longs rapports de travail instituée par l'art. 339b CO. Accordée au travailleur de plus de 50 ans qui a travaillé 20 ans au moins pour l'employeur, l'indemnité suisse avait, à l'origine, pour but d'inciter l'employeur à créer un système de prévoyance; elle a servi de transition jusqu'à ce que soit instituée la prévoyance obligatoire dans les entreprises (ATF 131 II 593 consid. 3.1 p. 601). Ne reposant pas sur la même conception, l'indemnité panaméenne n'apparaît pas comme un substitut à une prestation de prévoyance. Contrairement à ce que la cour cantonale laisse entendre, l'indemnité de départ panaméenne ne poursuit pas un objectif social et se présente bien plutôt comme une récompense de caractère purement patrimonial (cf. JÜRG EMIL EGLI, L'indemnité de départ dans le contrat de travail, 1979, p. 45).
        Le but de la disposition panaméenne en cause ne rentre ainsi pas dans les valeurs fondamentales de protection du travailleur. Au regard de la conception suisse du droit, l'intérêt du travailleur à obtenir l'indemnité de départ panaméenne ne peut être considéré comme légitime et prépondérant au point d'amener le juge suisse à prendre en considération, à titre exceptionnel, une norme impérative d'un Etat tiers sur la base de l'art. 19 LDIP. Le grief tiré d'une violation de cette disposition est dès lors fondé.
        Il s'ensuit que la cour cantonale n'avait pas à prendre en considération la loi panaméenne n° 8 et à accorder à l'intimé l'indemnité qu'il réclamait sur cette base.
        """

    thread_id = "court-analysis-test-002"

    # Initial analysis
    print("--- Initial Analysis ---")
    try:
        initial_response = analyse_court_decision(sample_decision, thread_id=thread_id)
        # Extract the actual content from the last AI message
        if initial_response and "messages" in initial_response and initial_response["messages"]:
             last_message = initial_response["messages"][-1]
             if isinstance(last_message, AIMessage):
                 print(last_message.content)
             else:
                 print("Agent did not return an AI message.")
        else:
            print("Invalid response format from agent.")

    except Exception as e:
        print(f"An error occurred during initial analysis: {e}")
        import traceback
        traceback.print_exc()


    print("\n--- Improving Summary ---")
    # Example feedback
    feedback = input(
        "Please provide your feedback on the initial analysis (e.g., 'Add more details about the court's position'):\n"
    )

    try:
        improved_response = improve_summary(feedback, thread_id=thread_id)
        # Extract the actual content from the last AI message
        if improved_response and "messages" in improved_response and improved_response["messages"]:
             last_message = improved_response["messages"][-1]
             if isinstance(last_message, AIMessage):
                 print(last_message.content)
             else:
                 print("Agent did not return an AI message.")
        else:
            print("Invalid response format from agent.")

    except Exception as e:
        print(f"An error occurred during improvement: {e}")
        import traceback
        traceback.print_exc()