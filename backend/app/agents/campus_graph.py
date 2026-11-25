import time
from typing import TypedDict, Any

from langgraph.graph import StateGraph, END

from app.agents.student_feedback_agent import analyze_student_feedback
from app.agents.resource_agent import analyze_resources
from app.agents.energy_agent import analyze_energy
from app.agents.scheduling_agent import analyze_schedule
from app.agents.administration_agent import analyze_administration
from app.agents.complaint_prioritizer import prioritize_complaint


# ==========================================
# CAMPUSIQ - LANGGRAPH STATE
# ==========================================

class CampusState(TypedDict, total=False):
    feedback: str
    resources: str
    energy: str
    schedule: str
    campus_data: str

    maintenance_title: str
    maintenance_description: str
    maintenance_category: str

    results: dict[str, Any]


# ==========================================
# INITIALIZE RESULTS
# ==========================================

def initialize_results(state: CampusState):
    return {"results": {}}


# ==========================================
# STUDENT FEEDBACK AGENT
# ==========================================

def student_feedback_node(state: CampusState):
    start_time = time.perf_counter()

    results = dict(state.get("results", {}))
    feedback = state.get("feedback", "").strip()

    if feedback:
        results["student_feedback"] = analyze_student_feedback(feedback)

    elapsed = time.perf_counter() - start_time
    print(f"[CampusIQ] Student Feedback Agent: {elapsed:.2f} seconds")

    return {"results": results}

# ==========================================
# RESOURCE MANAGEMENT AGENT
# ==========================================

def resource_node(state: CampusState):
    results = dict(state.get("results", {}))
    resources = state.get("resources", "").strip()

    if resources:
        results["resource_management"] = analyze_resources(resources)

    return {"results": results}


# ==========================================
# ENERGY ANALYSIS AGENT
# ==========================================

def energy_node(state: CampusState):
    results = dict(state.get("results", {}))
    energy = state.get("energy", "").strip()

    if energy:
        results["energy_analysis"] = analyze_energy(energy)

    return {"results": results}


# ==========================================
# SCHEDULING AGENT
# ==========================================

def scheduling_node(state: CampusState):
    results = dict(state.get("results", {}))
    schedule = state.get("schedule", "").strip()

    if schedule:
        results["scheduling"] = analyze_schedule(schedule)

    return {"results": results}


# ==========================================
# ADMINISTRATION AGENT
# ==========================================

def administration_node(state: CampusState):
    results = dict(state.get("results", {}))

    campus_data_parts = [
        state.get("campus_data", ""),
        state.get("feedback", ""),
        state.get("resources", ""),
        state.get("energy", ""),
        state.get("schedule", "")
    ]

    campus_data = " ".join(
        value.strip()
        for value in campus_data_parts
        if value and value.strip()
    )

    if campus_data:
        results["administration"] = analyze_administration(campus_data)

    return {"results": results}
# ==========================================
# MAINTENANCE AGENT
# ==========================================

def maintenance_node(state: CampusState):
    results = dict(state.get("results", {}))

    title = state.get("maintenance_title", "").strip()
    description = state.get("maintenance_description", "").strip()
    category = state.get("maintenance_category", "General")

    if title or description:
        results["maintenance"] = prioritize_complaint(
            title=title or "Campus maintenance request",
            description=description,
            category=category
        )

    return {"results": results}


# ==========================================
# BUILD LANGGRAPH WORKFLOW
# ==========================================

workflow = StateGraph(CampusState)

workflow.add_node("initialize", initialize_results)
workflow.add_node("student_feedback", student_feedback_node)
workflow.add_node("resource_management", resource_node)
workflow.add_node("energy_analysis", energy_node)
workflow.add_node("scheduling", scheduling_node)
workflow.add_node("administration", administration_node)
workflow.add_node("maintenance", maintenance_node)

workflow.set_entry_point("initialize")

workflow.add_edge("initialize", "student_feedback")
workflow.add_edge("student_feedback", "resource_management")
workflow.add_edge("resource_management", "energy_analysis")
workflow.add_edge("energy_analysis", "scheduling")
workflow.add_edge("scheduling", "administration")
workflow.add_edge("administration", "maintenance")
workflow.add_edge("maintenance", END)

campus_graph = workflow.compile()


# ==========================================
# PUBLIC ANALYSIS FUNCTION
# ==========================================

def analyze_campus(data: dict):
    result = campus_graph.invoke(data)

    return {
        "project": "CampusIQ",
        "status": "success",
        "agents_executed": list(result.get("results", {}).keys()),
        "results": result.get("results", {})
    }
