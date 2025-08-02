export let url =
    window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:8080"  // local dev
        : "https://api.irisxu.me";   // prod

export async function postMove(move) {
    try {
        const response = await fetch(url + "/move", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ move: move }),
        });

        if (response.ok) {
            //const data = await response.json();
            //console.log("Move updated cube in backend:", data);
        } else {
            console.error("Failed to send move to backend.");
        }
    } catch (error) {
        console.error("Error sending move to backend:", error);
    }
}

export async function getSolution() {
    try {
        const response = await fetch(url + "/solve", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });
        if (!response.ok) {
            throw new Error("Failed to fetch solution.");
        }
        const res = await response.json();
        return res;
    } catch (error) {
        console.error("Error fetching solution:", error);
        return null;
    }
}

export function resetBackendState() {
    fetch(url + '/reset-cube', { method: 'POST' })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to reset cube: " + response.statusText);
        }
    })
    .catch(error => console.error("Error resetting cube:", error));
}