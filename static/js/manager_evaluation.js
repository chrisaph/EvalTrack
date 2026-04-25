function getCSRFToken() {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
}

async function submitManagerEvaluation(evaluationId) {
    const inputs = document.querySelectorAll(".manager_actual");
    let objectives = [];
    let isValid = true;

    for (let input of inputs) {
        const value = parseFloat(input.value);
        const id = Number(input.dataset.id);

        if (!id) {
            alert("Internal error: Missing objective ID");
            return;
        }

        if (isNaN(value) || value < 0 || value > 110) {
            input.style.borderColor = '#ef4444';
            isValid = false;
        } else {
            input.style.borderColor = '#e5e7eb';
            objectives.push({ id, manager_actual: value });
        }
    }

    if (!isValid) {
        alert('Please enter valid percentages (0-110).');
        return;
    }

    const payload = {
        manager_comment: document.getElementById("manager_comment").value,
        objectives
    };

    try {
        const response = await fetch(`/api/evaluations/${evaluationId}/`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            alert("Saved!");
            window.location.href = "/manager/";
        } else {
            alert("Failed to save evaluation");
        }

    } catch (error) {
        alert("Network error.");
    }
}

document.querySelectorAll('.manager_actual').forEach(input => {
    input.addEventListener('input', function() {
        const value = parseFloat(this.value);
        this.style.borderColor =
            (isNaN(value) || value < 0 || value > 110)
            ? '#ef4444'
            : '#10b981';
    });
});

function goBack() {
    window.history.back();
}