import json
from dotenv import load_dotenv
import uuid
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated, List
from services.themes_extractor import fetch_themes_dataframe

# --- PROMPTS (minimal, inlined for this script) ---
COL_SECTION_PROMPT = """
Your task is to identify and extract the Choice of Law section from the original text of a court decision. To find and extract the choice of law section from a court decision, first, scan the headings and section titles for any terms that might be related to private international law. If no explicit section exists, search the text for key phrases such as \"this dispute shall be governed by,\" \"under the laws of,\" \"according to the law of,\" or references to private international law principles. Once identified, extract the relevant passages, ensuring they include any reasoning, statutory references, or precedents used by the court to determine the applicable law. You can return a maximum of two paragraphs. Most likely, it will be just one. In any case, it has to be a perfect copy of the text you find in the original version of the court decision.\n\nHere is the text of the Court Decision:\n{text}\n\nHere is the section of the Court Decision containing Choice of Law related information:\n
"""

PIL_THEME_PROMPT = """
Your task is to assign specific themes to a court decision. Your response consists of the most fitting value(s) from the \"Keywords\" column in the format \"keyword\". You assign the themes by finding the choice of law issue from the court decision and figuring out which Definition fits most. THE OUTPUT HAS TO BE ONE OR MULTIPLE OF THE VALUES FROM THE TABLE. Your output should adhere to the following format:\n[\"Theme 1\", \"Theme 2\"]\n\nHere is the table with all keywords and their definitions:\n{themes_table}\n\nHere is the text of the Court Decision:\n{text}\n\nHere is the section of the Court Decision containing Choice of Law related information:\n{quote}\n
"""

ANALYSIS_PROMPT = """
You are a jurist and a private international law expert. Analyze the following court decision.\nSummarize the key points in a concise paragraph, focusing on the Choice of Law section and the classified theme.\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{quote}\n\nClassified Theme(s): {classification}\n\nYour analysis:\n
"""

# --- THEMES TABLE (dynamic, from extractor) ---
def format_themes_table(df):
    if df.empty:
        return "No themes available."
    table_str = "| Theme | Definition |\n"
    table_str += "|-------|------------|\n"
    for _, row in df.iterrows():
        theme = str(row['Theme']).replace("|", "\\|")
        definition = str(row['Definition']).replace("|", "\\|")
        table_str += f"| {theme} | {definition} |\n"
    return table_str

THEMES_TABLE_DF = fetch_themes_dataframe()
THEMES_TABLE_STR = format_themes_table(THEMES_TABLE_DF)

# SAMPLE COURT DECISION
SAMPLE_COURT_DECISION = """
Urteilskopf

132 III 285

35. Auszug aus dem Urteil der I. Zivilabteilung i.S. X. AG gegen Y. (Berufung)
4C.1/2005 vom 20. Dezember 2005

Regeste

Art. 116 IPRG; Zulässigkeit der Rechtswahl.
Reglemente privatrechtlicher Vereine können nicht Gegenstand einer Rechtswahl im Sinne von Art. 116 IPRG sein. Sie können nur im Rahmen einer materiellrechtlichen Verweisung unter Berücksichtigung der zwingenden Bestimmungen des anwendbaren Sachrechts Vertragsinhalt werden (E. 1).
Die Vorschrift, wonach Forderungen binnen einer bestimmten Frist gerichtlich einzuklagen sind, verstösst gegen Art. 129 OR und ist daher unbeachtlich (E. 2).

Die X. AG mit Sitz in St. Gallen (Klägerin), vertreten durch einen FIFA-Agenten, schloss am 16. August 1999 mit der Y. mit Sitz in A. (Beklagte), einer griechischen Aktiengesellschaft, einen Vertrag über den Transfer eines von der Klägerin vertretenen Spielers. Gemäss dieser Vereinbarung sollte die Klägerin zunächst USD 15'000.-, zahlbar bis 30. September 1999, erhalten, sodann weitere USD 15'000.-, zahlbar bis 30. Dezember 1999, sofern der Arbeitsvertrag zwischen der Beklagten und dem Spieler bis zum 30. Juni 2000 verlängert würde, und schliesslich USD 30'000.-, zahlbar bis 30. Dezember 2000, und nochmals USD 30'000.-, zahlbar bis 30. Dezember 2001, sofern das Arbeitsverhältnis um weitere zwei Jahre verlängert würde.
Am 5. Februar 2003 reichte die Klägerin beim Handelsgericht des Kantons St. Gallen Klage ein und verlangte von der Beklagten ""US$ 15'000.- nebst 5 % Zins seit 30.09.99"", ""US$ 15'000.- nebst 5 % Zins seit 30.12.99"" und ""US$ 30'000.- nebst 5 % Zins seit 30.12.00"". Die Beklagte beteiligte sich nicht am Verfahren und reichte keine Klageantwort ein. Das Handelsgericht wies die Klage ab. Gegen dieses Urteil führt die Klägerin Berufung beim Bundesgericht. Sie beantragt, das angefochtene Urteil aufzuheben und hält an den bereits vor Handelsgericht gestellten Anträgen fest. Die Beklagte hat keine Berufungsantwort eingereicht.

Erwägungen

Aus den Erwägungen:

1. In Art. 3 des Vertrages vom 16. August 1999, auf welchen die Klägerin ihre Forderung stützt, haben die Parteien bestimmt, ihre Vereinbarung solle den FIFA-Regeln und dem Schweizer Recht unterstehen (""This agreement is governed by FIFA rules and Swiss law"").
Die Vorinstanz hat diese Vertragsklausel als kumulative Rechtswahl in dem Sinne interpretiert, dass die FIFA-Regeln dem nationalen schweizerischen Recht als lex specialis vorgehen sollten. Sie hat das Reglement angewendet, das die FIFA speziell für Spielervermittlungen am 10. Dezember 2000 erlassen hat und das ein Verfahren für Streitigkeiten vorsieht. Danach sind unter anderem Rechtsvorkehren spätestens zwei Jahre nach den zugrunde liegenden Vorfällen den zuständigen Organen einzureichen. Die Vorinstanz hat diese Bestimmung als Verwirkungsfrist interpretiert und die Klage mit der Begründung abgewiesen, im Zeitpunkt der Klageeinreichung sei die zweijährige Verwirkungsfrist bereits abgelaufen gewesen.
Die Klägerin rügt, die Vorinstanz habe Art. 116 Abs. 1 IPRG verletzt, denn das FIFA-Reglement könne nicht Gegenstand einer Rechtswahl sein.

1.1 Nach Art. 116 Abs. 1 IPRG untersteht der Vertrag dem gewählten Recht. Die Rechtswahl als kollisionsrechtliche Verweisung hat zur Folge, dass sowohl die dispositiven als auch die zwingenden Normen der gewählten Rechtsordnung zur Anwendung gelangen und die Bestimmungen des ohne Rechtswahl (im Rahmen einer ""objektiven"" Anknüpfung nach Art. 117 IPRG) anwendbaren Vertragsstatuts ersetzen (KELLER/KREN KOSTKIEWICZ, Zürcher Kommentar, N. 7 zu Art. 116 IPRG; AMSTUTZ/VOGT/WANG, Basler Kommentar, N. 11 zu Art. 116 IPRG mit Hinweisen). Dagegen lässt die materiellrechtliche Verweisung die gewählten Normen zum Vertragsinhalt werden. Sie ermöglicht den Parteien, ihre Rechtsbeziehung in den Schranken des anwendbaren Sachrechts frei zu gestalten (AMSTUTZ/VOGT/WANG, Basler Kommentar, N. 11 zu Art. 116 IPRG; KELLER/KREN KOSTKIEWICZ, Zürcher Kommentar, N. 8 und 83 ff. zu Art. 116 IPRG).

1.2 Ob die Parteien im Rahmen von Art. 116 Abs. 1 IPRG nur staatliche Rechtsordnungen wählen können oder ob auch die Wahl anationaler Normen zulässig ist, geht aus dem Wortlaut der Bestimmung nicht eindeutig hervor (BUCHER/BONOMI, Droit international privé, 2. Aufl., Basel/Genf/München 2004, S. 258 f.; VISCHER/ HUBER/OSER, Internationales Vertragsrecht, 2. Aufl., Bern 2000, S. 69), worauf schon in der Vernehmlassung zum Gesetzesentwurf hingewiesen wurde (vgl. Bundesgesetz über das internationale Privatrecht, Darstellung der Stellungnahmen auf Grund des Gesetzesentwurfs der Expertenkommission und des entsprechenden Begleitberichts, Bundesamt für Justiz 1980, S. 380 f.). Obwohl in der Botschaft im Vergleich zum Gesetzesentwurf der Expertenkommission eine minime redaktionelle Änderung vorgenommen wurde (vgl. BBl 1983 I 498, Art. 113; Eidg. Justizabteilung, Bundesgesetz über das internationale Privatrecht [IPR-Gesetz], Gesetzesentwurf der Expertenkommission und Begleitbericht, S. 29, Art. 117), erfolgte diesbezüglich keine Klarstellung. Die Expertenkommission selbst ging davon aus, die Wahl nichtstaatlicher Rechte sei ausgeschlossen (VISCHER, in: Freiburger Kolloquium über den Entwurf zu einem Bundesgesetz über das internationale Privatrecht, Zürich 1979, S. 49).
In der Lehre ist die Frage umstritten (zum deutschen Recht vgl. REITHMANN/MARTINY, Internationales Vertragsrecht, 6. Aufl., Köln 2004, S. 79 ff.). Ein Teil der Lehre spricht sich generell gegen die Gültigkeit kollisionsrechtlicher Verweisungen auf anationales Recht aus (SCHWANDER, Einführung in das internationale Privatrecht, Zweiter Band: Besonderer Teil, St. Gallen/Lachen 1997, N. 489, S. 227 f.; VINCENT BRULHART, Le choix de la loi applicable - questions choisies, Habilitationsschrift St. Gallen 2004, S. 254; KARRER, Basler Kommentar, N. 60 zu Art. 187 IPRG, allerdings unter anderem mit Hinweis auf HEINI, IPRG Kommentar, N. 7 zu Art. 187 IPRG, der die entsprechende Passage in der neuen Auflage des Kommentars nicht beibehalten hat, vgl. HEINI, Zürcher Kommentar, 2. Aufl., N. 7 zu Art. 187 IPRG; zweifelnd: KNOEPFLER/SCHWEIZER/OTHENIN-GIRARD, Droit international privé suisse, 3. Aufl., Bern 2005, S. 254, N. 499). Andere befürworten die Zulässigkeit generell (PATOCCHI, Das neue internationale Vertragsrecht der Schweiz, in: Internationales Privatrecht/Lugano-Abkommen, Zürich 1989, S. 36), in Bezug auf internationale Handelsbräuche (AMSTUTZ/VOGT/WANG, Basler Kommentar, N. 21 zu Art. 116 IPRG; vgl. auch BUCHER/BONOMI, a.a.O., S. 258) oder zumindest in Bezug auf bestimmte wissenschaftliche Regelungswerke, die bezüglich Ausgewogenheit, Anerkennung, und Regelungsdichte mit staatlichen Rechtsordnungen vergleichbar sind (VISCHER/HUBER/OSER, a.a.O., S. 67 ff.; VISCHER, Die kollisionsrechtliche Bedeutung der Wahl einer nichtstaatlichen Ordnung für den staatlichen Richter am Beispiel der Unidroit Principles of International Commercial Contracts, in: Schwenzer/Hager [Hrsg.], Festschrift für Peter Schlechtriem zum 70. Geburtstag, Tübingen 2003, S. 445 ff., insbesondere S. 451 f.; BERNARD DUTOIT, Droit international privé suisse: commentaire de la loi fédérale du 18 décembre 1987, 4. Aufl., Basel 2005, N. 12 zu Art. 116 IPRG, S. 384 f.; BUCHER/BONOMI, a.a.O., S. 258; AMSTUTZ/VOGT/WANG, Basler Kommentar, N. 21 zu Art. 116 IPRG; vgl. auch KURT SIEHR, Die Parteiautonomie im internationalen Privatrecht, in: Forstmoser/Giger/ Heini/Schluep [Hrsg.], Festschrift für Max Keller zum 65. Geburtstag, Zürich 1989, S. 501 f.).

1.3 Nach der Praxis des Bundesgerichts kommt Regelwerken privater Organisationen auch dann nicht die Qualität von Rechtsnormen zu, wenn sie sehr detailliert und ausführlich sind wie beispielsweise die SIA-Normen (BGE 126 III 388 E. 9d S. 391 mit Hinweisen) oder die Verhaltensregeln des internationalen Skiverbandes (BGE 122 IV 17 E. 2b/aa S. 20; BGE 106 IV 350 E. 3a S. 352, je mit Hinweisen). Von privaten Verbänden aufgestellte Bestimmungen stehen vielmehr grundsätzlich zu den staatlichen Gesetzen in einem Subordinationsverhältnis und können nur Beachtung finden, so weit das staatliche Recht für eine autonome Regelung Raum lässt (JÉRÔME JAQUIER, La qualification juridique des règles autonomes des organisations sportives, Diss. Neuenburg 2004, Rz. 212). Sie bilden kein ""Recht"" im Sinne von Art. 116 Abs. 1 IPRG und können auch nicht als ""lex sportiva transnationalis"" anerkannt werden, wie dies von einer Lehrmeinung befürwortet wird (JÉRÔME JAQUIER, a.a.O., Rz. 293 ff.). Die Regeln der (internationalen) Sportverbände können nur im Rahmen einer materiellrechtlichen Verweisung Anwendung finden und daher nur als Parteiabreden anerkannt werden, denen zwingende nationalrechtliche Bestimmungen vorgehen (KELLER/KREN KOSTKIEWICZ, Zürcher Kommentar, N. 84 zu Art. 116 IPRG).

1.4 Die Vorinstanz hat dem Verweis auf die FIFA-Regeln in Art. 3 des Vertrages vom 16. August 1999 bundesrechtswidrig die Bedeutung einer Rechtswahl zuerkannt. Dem Verweis auf das FIFA-Reglement kann nur die Bedeutung einer materiellrechtlichen Verweisung, d.h. einer (globalen) Übernahme in den Vertrag der Parteien zukommen. Dies widerspricht übrigens der Regelungsabsicht der FIFA nicht, weist doch die Präambel des FIFA-Reglements über die Spielervermittlungen vom 10. Dezember 2000 die Nationalverbände an, gestützt auf die Richtlinien verbandsinterne Reglemente zu erstellen (Ziffer 2) und bei deren Ausarbeitung die nationale Gesetzgebung und die internationalen Staatsverträge zu berücksichtigen (Ziffer 3). Die FIFA anerkennt damit die Subordination ihrer Verbandsregelung unter die massgebende nationalstaatliche Rechtsordnung mitsamt den internationalen Verträgen. Die Bestimmung in Ziffer 3 des Vertrages der Parteien ist als materiellrechtliche Verweisung zu verstehen, während die Rechtswahl sich allein auf die schweizerische Rechtsordnung bezieht, deren zwingende Normen somit Anwendung finden.

2. Nach herrschender Meinung verbietet Art. 129 OR eine vertragliche Verkürzung der Verjährungsfrist (VON TUHR/ESCHER, Allgemeiner Teil des schweizerischen Obligationenrechts, 3. Aufl., Zürich 1974, Bd. II, S. 217; SPIRO, Die Begrenzung privater Rechte durch Verjährungs-, Verwirkungs-, und Fatalfristen, Bern 1975, Bd. 1, S. 867 f.; DÄPPEN, Basler Kommentar, 3. Aufl., N. 5 zu Art. 129 OR; ENGEL, Traité des obligations en droit suisse: Dispositions générales du CO, 2. Aufl., Bern 1997, S. 809; PICHONNAZ, Commentaire romand, N. 5 zu Art. 129 CO; GAUCH/SCHLUEP/SCHMID/ REY, Schweizerisches Obligationenrecht, Allgemeiner Teil, Bd. II, 8. Aufl., Rz. 3566 mit Verweis auf BGE 63 II 180). Dies schliesst zwar nicht aus, dass eine Forderung von einer Resolutivbedingung abhängig gemacht werden kann. Allerdings ist eine Bedingung, wonach die Forderung binnen bestimmter Frist irgendwie gerichtlich einzuklagen sei, der Abkürzung der Verjährungsfrist gleichzustellen. Indem die Vorinstanz Art. 22 Abs. 3 des FIFA-Reglements im Ergebnis als Abkürzung der gesetzlichen Verjährungsfrist (Art. 127 OR) ausgelegt hat, hat sie die zwingende Norm von Art. 129 OR des schweizerischen Rechts missachtet, das die Parteien in Ziffer 3 des Vertrages gewählt haben. Der angefochtene Entscheid ist aus diesem Grund aufzuheben. Da die Vorinstanz keine Feststellungen zur materiellen Begründetheit der eingeklagten Forderung getroffen hat, ist die Sache zur Neubeurteilung gestützt auf Art. 64 Abs. 1 OG an die Vorinstanz zurückzuweisen.
"""

# --- STATE SCHEMA ---
class AppState(TypedDict):
    full_text: str
    quote: str
    classification: List[str]
    user_approved_col: bool
    col_section_feedback: Annotated[List[str], add_messages]
    user_approved_theme: bool
    theme_feedback: Annotated[List[str], add_messages]
    analysis: str
    user_approved_analysis: bool
    final_feedback: Annotated[List[str], add_messages]

# --- LLM SETUP ---
load_dotenv()
llm = ChatOpenAI(model="gpt-4.1-nano")

# --- GRAPH NODES ---
def col_section_node(state: AppState):
    print("\n--- COL SECTION EXTRACTION ---")
    #print("State \n", state)
    text = state["full_text"]
    col_section_feedback = state["col_section_feedback"] if "col_section_feedback" in state else ["No feedback yet"]
    prompt = COL_SECTION_PROMPT.format(text=text)
    if col_section_feedback:
        prompt += f"\n\nPrevious feedback: {col_section_feedback[-1]}\n"
    #print(f"\nPrompt for CoL section extraction:\n{prompt}\n")
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    quote = response.content
    print(f"\nExtracted Choice of Law section:\n{quote}\n")
    return {
        "quote": [AIMessage(content=quote)],
        "col_section_feedback": col_section_feedback
    }

def col_section_feedback_node(state: AppState):
    print("\n--- USER FEEDBACK: COL SECTION ---")
    #print("State \n", state)
    col_section_feedback = interrupt(
        {
            "col_section": state["quote"],
            "message": "Provide feedback for the Choice of Law section or type 'continue' to proceed with the analysis: ",
            "workflow": "col_section_feedback"
        }
    )
    
    if col_section_feedback.lower() == "continue":
        return Command(update={"user_approved_col": True, "col_section_feedback": state["col_section_feedback"] + ["Finalised"]}, goto="theme_classification_node")
    
    return Command(update={"col_section_feedback": state["col_section_feedback"] + [col_section_feedback]}, goto="col_section_node")

def theme_classification_node(state: AppState):
    print("\n--- THEME CLASSIFICATION ---")
    #print("State \n", state)
    text = state["full_text"]
    quote = state["quote"]
    theme_feedback = state["theme_feedback"] if "theme_feedback" in state else ["No feedback yet"]
    prompt = PIL_THEME_PROMPT.format(text=text, quote=quote, themes_table=THEMES_TABLE_STR)
    if theme_feedback:
        prompt += f"\n\nPrevious feedback: {theme_feedback[-1]}\n"
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    try:
        classification = json.loads(response.content)
    except Exception:
        classification = [response.content.strip()]
    print(f"\nClassified theme(s): {classification}\n")
    return {"classification": [AIMessage(content=classification)], "theme_feedback": theme_feedback}

def theme_feedback_node(state: AppState):
    print("\n--- USER FEEDBACK: THEME ---")
    #print("State \n", state)
    theme_feedback = interrupt(
        {
            "classification": state["classification"],
            "message": "Provide feedback for the Private International Law classification or type 'continue' to proceed with the analysis: ",
            "workflow": "theme_feedback"
        }
    )
    if theme_feedback.lower() == "continue":
        return Command(update={"user_approved_theme": True}, goto="analysis_node")
    
    return Command(update={"user_approved_theme": False, "theme_feedback": state["theme_feedback"] + [theme_feedback]}, goto="theme_classification_node")

def analysis_node(state: AppState):
    print("\n--- ANALYSIS ---")
    #print("State \n", state)
    text = state["full_text"]
    quote = state["quote"]
    classification = state["classification"]
    prompt = ANALYSIS_PROMPT.format(text=text, quote=quote, classification=classification)
    analysis_feedback = state["analysis"] if "analysis" in state else ["No feedback yet"]
    if analysis_feedback:
        prompt += f"\n\nPrevious feedback: {analysis_feedback[-1]}\n"
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    analysis = response.content
    print(f"\nAnalysis:\n{analysis}\n")
    return {"analysis": [AIMessage(content=analysis)], "analysis_feedback": analysis_feedback}

def final_feedback_node(state: AppState):
    print("\n--- USER FEEDBACK: FINAL ANALYSIS ---")
    #print("State \n", state)
    final_feedback = interrupt(
        {
            "analysis": state["analysis"],
            "message": "Provide feedback for the analysis or type 'done' to finish.",
            "workflow": "final_feedback"
        }
    )
    if final_feedback.lower() == "done":
        return Command(update={"user_approved_analysis": True}, goto=END)
    return Command(update={"user_approved_analysis": False, "final_feedback": state["final_feedback"] + [final_feedback]}, goto="analysis_node")

# --- GRAPH DEFINITION ---
graph = StateGraph(AppState)
graph.add_node("col_section_node", col_section_node)
graph.add_node("col_section_feedback_node", col_section_feedback_node)
graph.add_node("theme_classification_node", theme_classification_node)
graph.add_node("theme_feedback_node", theme_feedback_node)
graph.add_node("analysis_node", analysis_node)
graph.add_node("final_feedback_node", final_feedback_node)

graph.set_entry_point("col_section_node")

graph.add_edge(START, "col_section_node")
graph.add_edge("col_section_node", "col_section_feedback_node")
graph.add_edge("theme_classification_node", "theme_feedback_node")
graph.add_edge("analysis_node", "final_feedback_node")
#graph.add_edge("final_feedback_node", END)

#graph.set_finish_point("final_feedback_node")

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

#print(app.get_graph().draw_ascii())

thread_config = {"configurable": {"thread_id": str(uuid.uuid4())}}

full_text = SAMPLE_COURT_DECISION
initial_state = {
    "full_text": SAMPLE_COURT_DECISION,
    "quote": "",
    "classification": [],
    "user_approved_col": False,
    "user_approved_theme": False,
    "analysis": ""
}

events = app.stream(initial_state, config=thread_config, stream_mode="values")

i = 1
for event in events:
    print(f"Event {i}\n\n")
    i += 1
    print(event)


"""
for chunk in app.stream(initial_state, config=thread_config):
    for node_id, value in chunk.items():
        if node_id == "__interrupt__" and value[0].value['workflow'] == "col_section_feedback":
            print("col_section_feedback detected, now waiting for user feedback...")
            while True:
                user_col_feedback = input(value[0].value['message'])

                app.invoke(Command(resume=user_col_feedback), config=thread_config)

                if user_col_feedback.lower() == "continue":
                    pass
        if node_id == "__interrupt__" and value[0].value['workflow'] == "theme_feedback":
            print("theme_feedback detected, now waiting for user feedback...")
            while True:
                user_theme_feedback = input(value[0].value['message'])

                app.invoke(Command(resume=user_theme_feedback), config=thread_config)

                if user_theme_feedback.lower() == "continue":
                    pass
        if node_id == "__interrupt__" and value[0].value['workflow'] == "final_feedback":
            print("final_feedback detected, now waiting for user feedback...")
            while True:
                user_final_feedback = input(value[0].value['message'])

                app.invoke(Command(resume=user_final_feedback), config=thread_config)

                if user_final_feedback.lower() == "done":
                    break
"""