
// ==========================================
// CAMPUSIQ - FRONTEND AND BACKEND CONNECTION
// ==========================================
const API_URL = "";

// ==========================================
// 1. LOAD DASHBOARD ANALYTICS
// ==========================================

async function loadDashboardStats() {
    const categoryContainer =
        document.getElementById("categoryBreakdown");

    try {
        const response = await fetch(
            `${API_URL}/api/maintenance/stats`
        );

        if (!response.ok) {
            throw new Error("Unable to load dashboard statistics");
        }

        const stats = await response.json();

        const categories = stats.category_breakdown || [];

        // Update all KPI cards
        document.getElementById("totalRequestsValue").textContent =
            stats.total_requests ?? 0;

        document.getElementById("pendingRequestsValue").textContent =
            stats.pending_requests ?? 0;

        document.getElementById("highPriorityValue").textContent =
            stats.high_priority_requests ?? 0;

        document.getElementById("categoryCountValue").textContent =
            categories.length;

        document.getElementById("inProgressRequestsValue").textContent =
            stats.in_progress_requests ?? 0;

        document.getElementById("resolvedRequestsValue").textContent =
            stats.resolved_requests ?? 0;

        // Update category analytics
        if (!categoryContainer) return;

        categoryContainer.innerHTML = "";

        if (categories.length === 0) {
            categoryContainer.innerHTML =
                '<p class="category-empty">No maintenance requests yet.</p>';
            return;
        }

        const maxCount = Math.max(
            ...categories.map(item => item.count)
        );

        categories.forEach(item => {
            const percentage = maxCount > 0
                ? (item.count / maxCount) * 100
                : 0;

            const row = document.createElement("div");
            row.className = "category-row";

            row.innerHTML = `
                <div class="category-info">
                    <strong></strong>
                    <span></span>
                </div>
                <div class="category-progress">
                    <div class="category-progress-fill"></div>
                </div>
            `;

            row.querySelector("strong").textContent =
                item.category;

            row.querySelector(".category-info span").textContent =
                `${item.count} requests`;

            row.querySelector(".category-progress-fill").style.width =
                `${percentage}%`;

            categoryContainer.appendChild(row);
        });

    } catch (error) {
        console.error("Dashboard analytics error:", error);

        if (categoryContainer) {
            categoryContainer.innerHTML =
                '<p class="category-empty">Unable to load category analytics.</p>';
        }
    }
}

// ==========================================
// 2. LOAD MAINTENANCE REQUESTS
// ==========================================

async function loadMaintenanceRequests() {

    const tableBody =
        document.getElementById("maintenanceTableBody");

    const countElement =
        document.getElementById("maintenanceCount");

    const navCountElement =
        document.getElementById("maintenanceNavCount");

    if (!tableBody) return;

    try {
        const response = await fetch(
            `${API_URL}/api/maintenance/`
        );

        if (!response.ok) {
            throw new Error("Unable to load maintenance requests");
        }

        const requests = await response.json();

        tableBody.innerHTML = "";

        requests.forEach(request => {

            const row = document.createElement("tr");

            const values = [
                request.request_code,
                request.title,
                request.location,
                request.category,
                request.priority,
                new Date(request.created_at).toLocaleDateString()
            ];

            // Create table cells
            values.forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value ?? "";
                row.appendChild(cell);
            });

            // CREATE STATUS DROPDOWN
            const statusCell = document.createElement("td");

            const statusSelect = document.createElement("select");
            statusSelect.className = "status-select";

            const allowedStatuses = [
                "Pending",
                "In Progress",
                "Resolved"
            ];

            allowedStatuses.forEach(status => {

                const option = document.createElement("option");

                option.value = status;
                option.textContent = status;

                if (status === request.status) {
                    option.selected = true;
                }

                statusSelect.appendChild(option);
            });

            // SAVE STATUS TO DATABASE
            statusSelect.addEventListener("change", async function() {

                const newStatus = this.value;

                statusSelect.disabled = true;

                try {
                    const updateResponse = await fetch(
                        `${API_URL}/api/maintenance/${request.id}/status`,
                        {
                            method: "PATCH",
                            headers: {
                                "Content-Type": "application/json"
                            },
                            body: JSON.stringify({
                                status: newStatus
                            })
                        }
                    );

                    if (!updateResponse.ok) {
                        throw new Error(
                            "Unable to update request status"
                        );
                    }

                    alert(
                        "Maintenance status updated successfully!"
                    );

                    await loadMaintenanceRequests();
                    await loadDashboardStats();

                } catch (error) {
                    console.error("Status update error:", error);

                    alert(
                        "Status update failed. Please try again."
                    );

                    await loadMaintenanceRequests();

                } finally {
                    statusSelect.disabled = false;
                }
            });

            
statusCell.appendChild(statusSelect);
row.appendChild(statusCell);

// ACTION COLUMN - DELETE BUTTON
const actionCell = document.createElement("td");

const deleteButton = document.createElement("button");
deleteButton.textContent = "Delete";
deleteButton.type = "button";
deleteButton.className = "delete-btn";

deleteButton.addEventListener("click", async function() {

    const confirmDelete = confirm(
        `Are you sure you want to delete ${request.request_code}?`
    );

    if (!confirmDelete) return;

    deleteButton.disabled = true;
    deleteButton.textContent = "Deleting...";

    try {
        const deleteResponse = await fetch(
            `${API_URL}/api/maintenance/${request.id}`,
            {
                method: "DELETE"
            }
        );

        if (!deleteResponse.ok) {
            throw new Error("Unable to delete maintenance request");
        }

        alert("Maintenance request deleted successfully!");

        await loadMaintenanceRequests();
        await loadDashboardStats();

    } catch (error) {
        console.error("Delete error:", error);

        alert("Delete failed. Please try again.");

        deleteButton.disabled = false;
        deleteButton.textContent = "Delete";
    }
});

actionCell.appendChild(deleteButton);
row.appendChild(actionCell);

tableBody.appendChild(row);

        });

        // Update maintenance counts
        if (countElement) {
            countElement.textContent = requests.length;
        }

        if (navCountElement) {
            navCountElement.textContent = requests.length;
        }

        const agentCountElement =
            document.getElementById("maintenanceAgentCount");

        if (agentCountElement) {
            agentCountElement.textContent =
                `Tracking ${requests.length} requests`;
        }

    } catch (error) {
        console.error("Maintenance loading error:", error);

        tableBody.innerHTML =
            '<tr><td colspan="7">Unable to load requests. Check backend connection.</td></tr>';
    }
}


// ==========================================
// 3. AI ANALYSIS PANEL AND REQUEST SUBMISSION
// ==========================================

const maintenanceForm =
    document.getElementById("maintenanceForm");

let pendingMaintenanceRequest = null;
let pendingAIAnalysis = null;

const aiAnalysisPanel =
    document.getElementById("aiAnalysisPanel");

const aiPriority =
    document.getElementById("aiPriority");

const aiDepartment =
    document.getElementById("aiDepartment");

const aiReason =
    document.getElementById("aiReason");

const analyzeRequestBtn =
    document.getElementById("analyzeRequestBtn");

const confirmAIRequest =
    document.getElementById("confirmAIRequest");

const cancelAIRequest =
    document.getElementById("cancelAIRequest");


// ==========================================
// 3A. ANALYZE COMPLAINT
// ==========================================

if (maintenanceForm) {

    maintenanceForm.addEventListener("submit", async function(event) {

        event.preventDefault();

        const requestData = {
            title: document.getElementById("issueTitle").value.trim(),
            location: document.getElementById("issueLocation").value.trim(),
            category: document.getElementById("issueCategory").value,
            priority: document.getElementById("issuePriority").value,
            description: document.getElementById("issueDescription").value.trim()
        };

        if (analyzeRequestBtn) {
            analyzeRequestBtn.disabled = true;
            analyzeRequestBtn.textContent = "AI Analyzing...";
        }

        if (aiAnalysisPanel) {
            aiAnalysisPanel.hidden = true;
        }

        try {
            const response = await fetch(
                `${API_URL}/api/maintenance/analyze`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(requestData)
                }
            );

            const result = await response.json();

            if (!response.ok) {
                throw new Error(
                    result.detail
                        ? JSON.stringify(result.detail)
                        : "AI analysis failed"
                );
            }

            const analysis = result.analysis;

            // Store data until user confirms submission
            pendingMaintenanceRequest = requestData;
            pendingAIAnalysis = analysis;

            // Display AI recommendations
            if (aiPriority) {
                aiPriority.textContent =
                    analysis.recommended_priority;
            }

            if (aiDepartment) {
                aiDepartment.textContent =
                    analysis.recommended_department;
            }

            if (aiReason) {
                aiReason.textContent =
                    analysis.reason;
            }

            if (aiAnalysisPanel) {
                aiAnalysisPanel.hidden = false;
            }
            if (confirmAIRequest) {
             confirmAIRequest.disabled = false;
            }

            if (analyzeRequestBtn) {
                analyzeRequestBtn.hidden = true;
            }

        } catch (error) {
            console.error("AI analysis error:", error);

            alert(
                "Unable to analyze complaint. " + error.message
            );

        } finally {
            if (analyzeRequestBtn) {
                analyzeRequestBtn.disabled = false;
                analyzeRequestBtn.textContent =
                    "Analyze with CampusIQ AI";
            }
        }
    });
}


// 
// ==========================================
// 3B. CONFIRM AND SAVE REQUEST
// ==========================================

if (confirmAIRequest) {

    confirmAIRequest.addEventListener("click", async function() {

        if (!pendingMaintenanceRequest || !pendingAIAnalysis) {
            alert("Please analyze the complaint first.");
            return;
        }

        confirmAIRequest.disabled = true;
        confirmAIRequest.textContent = "Saving Request...";

        const finalRequestData = {
            ...pendingMaintenanceRequest,
            priority: pendingAIAnalysis.recommended_priority
        };

        try {
            const response = await fetch(
                `${API_URL}/api/maintenance/`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(finalRequestData)
                }
            );

            const result = await response.json();

            if (!response.ok) {
                throw new Error(
                    result.detail
                        ? JSON.stringify(result.detail)
                        : "Request submission failed"
                );
            }

            alert(
                "Maintenance request submitted successfully!\n\n" +
                "Request ID: " + result.request_code +
                "\nAI Priority: " +
                pendingAIAnalysis.recommended_priority
            );

            // Reset maintenance form
            maintenanceForm.reset();

            // Clear pending AI data
            pendingMaintenanceRequest = null;
            pendingAIAnalysis = null;

            // Hide AI analysis panel
            if (aiAnalysisPanel) {
                aiAnalysisPanel.hidden = true;
            }

            // Show Analyze button again
            if (analyzeRequestBtn) {
                analyzeRequestBtn.hidden = false;
            }

            // Refresh maintenance table and dashboard
            await loadMaintenanceRequests();
            await loadDashboardStats();

        } catch (error) {
            console.error("Request submission error:", error);

            alert(
                "Unable to submit request. " + error.message
            );

        } finally {
            confirmAIRequest.disabled = false;
            confirmAIRequest.textContent = "Confirm & Submit";
        }
    });
}

// ==========================================
// 3C. CANCEL AI ANALYSIS
// ==========================================

if (cancelAIRequest) {

    cancelAIRequest.addEventListener("click", function() {

        pendingMaintenanceRequest = null;
        pendingAIAnalysis = null;

        if (aiAnalysisPanel) {
            aiAnalysisPanel.hidden = true;
        }

        if (analyzeRequestBtn) {
            analyzeRequestBtn.hidden = false;
            analyzeRequestBtn.disabled = false;
            analyzeRequestBtn.textContent =
                "Analyze with CampusIQ AI";
        }
    });
}


// ==========================================
// 4. CAMPUSIQ SIX-AGENT CAMPUS ANALYSIS
// ==========================================

// Sample campus information for the first integration test.
// These values can later be replaced with user-entered data.

// Stores the latest successful campus analysis for report export.
let latestCampusAnalysis = null;
function getCampusAnalysisData() {
    return {
        feedback: document.getElementById("feedbackInput").value.trim(),

        resources: document.getElementById("resourcesInput").value.trim(),

        energy: document.getElementById("energyInput").value.trim(),

        schedule: document.getElementById("scheduleInput").value.trim(),

        campus_data: document.getElementById("campusDataInput").value.trim(),

        maintenance_title: document.getElementById("maintenanceTitleInput").value.trim(),

        maintenance_description: document.getElementById("maintenanceDescriptionInput").value.trim(),

        maintenance_category: document.getElementById("maintenanceCategoryInput").value
    };
}

// Create a heading and list for agent findings.

function addAgentList(card, heading, items) {

    if (!Array.isArray(items) || items.length === 0) {
        return;
    }

    const section = document.createElement("div");
    section.className = "agent-result-details";

    const title = document.createElement("strong");
    title.textContent = heading;

    const list = document.createElement("ul");

    items.forEach(item => {
        const li = document.createElement("li");
        li.textContent = item;
        list.appendChild(li);
    });

    section.appendChild(title);
    section.appendChild(list);

    card.appendChild(section);
}


// Display individual agent results.

function renderCampusInsights(results) {

    const container =
        document.getElementById("campusInsightsResults");

    if (!container) return;

    container.innerHTML = "";

    const agentConfigurations = [
        {
            key: "student_feedback",
            title: "Student Feedback Agent",
            fields: [
                ["Positive Points", "positive_points"],
                ["Student Issues", "issues"],
                ["Recommendations", "recommendations"]
            ]
        },
        {
            key: "resource_management",
            title: "Resource Management Agent",
            fields: [
                ["Resource Issues", "resource_issues"],
                ["Recommendations", "recommendations"]
            ]
        },
        {
            key: "energy_analysis",
            title: "Energy Analysis Agent",
            fields: [
                ["Energy Issues", "energy_issues"],
                ["Recommendations", "recommendations"]
            ]
        },
        {
            key: "scheduling",
            title: "Scheduling Agent",
            fields: [
                ["Detected Conflicts", "conflicts"],
                ["Recommendations", "recommendations"]
            ]
        },
        {
            key: "administration",
            title: "Administration Agent",
            fields: [
                ["Key Findings", "key_findings"],
                ["Recommendations", "recommendations"]
            ]
        }
    ];

    agentConfigurations.forEach(config => {

        const agent = results[config.key];

        if (!agent) return;

        const card = document.createElement("div");
        card.className = "insight-card";

        const type = document.createElement("div");
        type.className = "insight-type success";
        type.textContent = "✦ AGENT ANALYSIS";

        const title = document.createElement("strong");
        title.textContent = config.title;

        const summary = document.createElement("p");
        summary.textContent =
            agent.summary || "Analysis completed.";

        card.appendChild(type);
        card.appendChild(title);
        card.appendChild(summary);

        config.fields.forEach(([heading, field]) => {
            addAgentList(card, heading, agent[field]);
        });

        container.appendChild(card);
    });


    // Maintenance Agent has a different response structure.

    const maintenance = results.maintenance;

    if (maintenance) {

        const card = document.createElement("div");
        card.className = "insight-card";

        const type = document.createElement("div");
        type.className = "insight-type warning";
        type.textContent = "⚠ MAINTENANCE ANALYSIS";

        const title = document.createElement("strong");
        title.textContent = "Maintenance Agent";

        const priority = document.createElement("p");
        priority.textContent =
            "Recommended Priority: " +
            (maintenance.recommended_priority || "Not available");

        const department = document.createElement("p");
        department.textContent =
            "Assigned Department: " +
            (maintenance.recommended_department || "Not available");

        const reason = document.createElement("p");
        reason.textContent =
            "Reason: " + (maintenance.reason || "Not available");

        card.appendChild(type);
        card.appendChild(title);
        card.appendChild(priority);
        card.appendChild(department);
        card.appendChild(reason);

        container.appendChild(card);
    }
}
// ==========================================
// DOWNLOAD CAMPUSIQ ANALYSIS REPORT
// ==========================================

function downloadCampusReport() {

    if (!latestCampusAnalysis) {
        alert("Please run campus analysis before downloading a report.");
        return;
    }

    const input = latestCampusAnalysis.input || {};
    const results = latestCampusAnalysis.results || {};
    const agents = latestCampusAnalysis.agentsExecuted || [];

    const generatedDate = new Date();

    let report = "";

    // REPORT HEADER
    report += "==================================================\n";
    report += "       CAMPUSIQ - SMART CAMPUS MANAGEMENT\n";
    report += "              AI ANALYSIS REPORT\n";
    report += "==================================================\n\n";

    report += `Generated Date: ${generatedDate.toLocaleDateString()}\n`;
    report += `Generated Time: ${generatedDate.toLocaleTimeString()}\n`;
    report += `Total AI Agents Executed: ${agents.length}\n\n`;

    report += "AI AGENTS:\n";
    agents.forEach((agent, index) => {
        report += `${index + 1}. ${String(agent).replace(/_/g, " ")}\n`;
    });

    // CAMPUS INFORMATION
    report += "\n\n==================================================\n";
    report += "1. CAMPUS INFORMATION\n";
    report += "==================================================\n";

    const inputLabels = {
        feedback: "Student Feedback",
        resources: "Resource Information",
        energy: "Energy Consumption",
        schedule: "Scheduling Information",
        campus_data: "General Campus Information",
        maintenance_title: "Maintenance Issue Title",
        maintenance_description: "Maintenance Description",
        maintenance_category: "Maintenance Category"
    };

    Object.entries(inputLabels).forEach(([key, label]) => {

        report += `\n${label}:\n`;
        report += `${input[key] || "Not provided"}\n`;

    });

    // AI AGENT RESULTS
    report += "\n\n==================================================\n";
    report += "2. AI AGENT ANALYSIS RESULTS\n";
    report += "==================================================\n";

    Object.entries(results).forEach(([agentName, agentData], index) => {

        report += `\n\n${index + 1}. ${agentName.replace(/_/g, " ").toUpperCase()}\n`;
        report += "--------------------------------------------------\n";

        if (!agentData || typeof agentData !== "object") {
            report += String(agentData ?? "No results available") + "\n";
            return;
        }

        Object.entries(agentData).forEach(([key, value]) => {

            const label = key.replace(/_/g, " ").toUpperCase();

            report += `\n${label}:\n`;

            if (Array.isArray(value)) {

                report += value.length
                    ? value.map(item => `  - ${typeof item === "object" ? JSON.stringify(item) : item}`).join("\n")
                    : "  No information available";

            } else if (value !== null && typeof value === "object") {

                report += JSON.stringify(value, null, 2);

            } else {

                report += String(value ?? "Not available");

            }

            report += "\n";
        });

    });

    // REPORT FOOTER
    report += "\n\n==================================================\n";
    report += "              END OF REPORT\n";
    report += "==================================================\n";
    report += "Generated by CampusIQ Smart Campus Management System\n";

    // DOWNLOAD FILE
    const blob = new Blob(
        [report],
        { type: "text/plain;charset=utf-8" }
    );

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download =
        `CampusIQ_Report_${generatedDate.toISOString().slice(0, 10)}.txt`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setTimeout(() => URL.revokeObjectURL(url), 1000);

    console.log("CampusIQ report downloaded successfully.");
}
// ==========================================
// RUN CAMPUS ANALYSIS
// Calls the LangGraph Campus Insights API
// ==========================================

async function runCampusAnalysis() {

    const button = document.getElementById("runCampusAnalysisBtn");
    const status = document.getElementById("campusAnalysisStatus");

    if (!button || !status) {
        console.error("Campus Analysis button or status element not found.");
        return;
    }

    button.disabled = true;
    button.classList.add("is-loading");
    button.textContent = "Analyzing Campus...";
    status.textContent = "Preparing campus information...";

    try {

        // Collect campus information
        const analysisData = getCampusAnalysisData();

        // Check whether the user entered any information
        const hasInput = Object.entries(analysisData).some(
            ([key, value]) =>
                key !== "maintenance_category" &&
                String(value || "").trim() !== ""
        );

        if (!hasInput) {
            status.textContent =
                "Please enter at least one campus detail before analysis.";

            button.textContent = "Run Campus Analysis";
            return;
        }

        status.textContent =
            "CampusIQ agents are analyzing campus information. Please wait...";

        // Send request to FastAPI backend
        const response = await fetch(
            `${API_URL}/api/campus/analyze`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(analysisData)
            }
        );

        // Safely read API response
        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Campus analysis failed."
            );
        }

        // Validate response
        if (
            data.status !== "success" ||
            !data.results
        ) {
            throw new Error(
                "Campus analysis returned an unexpected response."
            );
        }

        // Store latest analysis
        latestCampusAnalysis = {
            input: analysisData,
            results: data.results,
            agentsExecuted: data.agents_executed || []
        };

        // Display AI agent results
        renderCampusInsights(data.results);

        // Enable report download if button exists
        const downloadButton =
            document.getElementById("downloadCampusReportBtn");

        if (downloadButton) {
            downloadButton.disabled = false;
        }

        status.textContent =
            `Analysis completed successfully! ${
                (data.agents_executed || []).length
            } AI agents executed.`;

        button.textContent = "↻ Run Analysis Again";

    } catch (error) {

        console.error("CampusIQ analysis error:", error);

        status.textContent =
            "Unable to complete campus analysis: " + error.message;

        button.textContent = "Try Again";

    } finally {

        // Always enable the button again
        button.disabled = false;

    }
}

// ==========================================
// DOWNLOAD CAMPUS ANALYSIS REPORT
// ==========================================

// ==========================================
// 4. LOAD DATA WHEN PAGE OPENS
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("CampusIQ dashboard loaded successfully!");

    // Load Maintenance Requests
    loadMaintenanceRequests();

    // Load Dashboard Statistics
    loadDashboardStats();


    // ==========================================
    // RUN CAMPUS ANALYSIS BUTTON
    // ==========================================

    const runCampusAnalysisBtn =
        document.getElementById("runCampusAnalysisBtn");

    if (runCampusAnalysisBtn) {

        runCampusAnalysisBtn.addEventListener("click", function (event) {

            event.preventDefault();

            console.log("Campus Analysis button clicked!");

            runCampusAnalysis();

        });

    } else {

        console.error("Campus Analysis button not found!");

    }


    // ==========================================
    // DOWNLOAD CAMPUS REPORT BUTTON
    // ==========================================

    const downloadCampusReportBtn =
        document.getElementById("downloadCampusReportBtn");

    if (downloadCampusReportBtn) {

        downloadCampusReportBtn.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                console.log("Download Campus Report button clicked!");

                downloadCampusReport();

            }
        );

    }


    console.log("All dashboard event listeners initialized!");

});
// ==========================================
// 5. CAMPUSIQ AI CHAT ASSISTANT
// ==========================================

let chatHistory = [];

function appendChatMessage(role, content, extraClass = "") {

    const messages = document.getElementById("chatMessages");

    if (!messages) return null;

    const message = document.createElement("div");

    message.className =
        `chat-message ${role}-message ${extraClass}`.trim();

    const avatar = document.createElement("div");
    avatar.className = "chat-avatar";
    avatar.textContent = role === "user" ? "You" : "AI";

    const bubble = document.createElement("div");
    bubble.className = "chat-bubble";

    const heading = document.createElement("strong");
    heading.textContent =
        role === "user" ? "You" : "CampusIQ Assistant";

    const paragraph = document.createElement("p");
    paragraph.textContent = content;

    bubble.appendChild(heading);
    bubble.appendChild(paragraph);

    message.appendChild(avatar);
    message.appendChild(bubble);

    messages.appendChild(message);

    messages.scrollTop = messages.scrollHeight;

    return message;
}


async function sendChatMessage(event) {

    event.preventDefault();

    const input = document.getElementById("chatInput");
    const button = document.getElementById("chatSendBtn");

    if (!input || !button) return;

    const message = input.value.trim();

    if (!message) return;

    // Display the user's message.
    appendChatMessage("user", message);

    // Save the user's message in conversation history.
    chatHistory.push({
        role: "user",
        content: message
    });

    input.value = "";
    button.disabled = true;
    button.textContent = "Thinking...";

    // Display a temporary loading message.
    const loadingMessage = appendChatMessage(
        "assistant",
        "Thinking... Please wait."
    );

    try {

        const response = await fetch(
            `${API_URL}/api/chat/`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    message: message,
                    history: chatHistory.slice(0, -1)
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "AI Assistant request failed."
            );
        }

        if (!data.reply) {
            throw new Error("The AI Assistant returned an empty response.");
        }

        // Remove the temporary loading message.
        if (loadingMessage) {
            loadingMessage.remove();
        }

        // Display the AI response.
        appendChatMessage("assistant", data.reply);

        // Save the AI response for future questions.
        chatHistory.push({
            role: "assistant",
            content: data.reply
        });

    } catch (error) {

        console.error("CampusIQ Chat Error:", error);

        if (loadingMessage) {
            loadingMessage.remove();
        }

        // Remove the failed user message from history.
        chatHistory.pop();

        appendChatMessage(
            "assistant",
            "Unable to connect to the AI Assistant. Please check that the backend and Ollama are running, then try again.",
            "chat-error"
        );

    } finally {

        button.disabled = false;
        button.textContent = "Send";
        input.focus();

    }
}


// Register the chat form without changing existing handlers.
document.addEventListener("DOMContentLoaded", function() {

    const chatForm = document.getElementById("chatForm");

    if (chatForm) {
        chatForm.addEventListener("submit", sendChatMessage);
    }

});

