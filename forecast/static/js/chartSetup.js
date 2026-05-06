document.addEventListener("DOMContentLoaded", () => {
    const chartElement = document.getElementById("chart");
    if (!chartElement) {
        console.error("Canvas element not found");
        return;
    }

    const ctx = chartElement.getContext("2d");
    if (!ctx) {
        console.error("Canvas context not available");
        return;
    }

    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
    gradient.addColorStop(0, "rgba(250, 0, 0, 1)");
    gradient.addColorStop(1, "rgba(136, 255, 0, 1)");

    const forecastItems = document.querySelectorAll(".forecast-item");
    const times = [];
    const temps = [];

    forecastItems.forEach((item) => {
        const time = item.querySelector(".forecast-time")?.textContent.trim();
        const tempText = item.querySelector(".forecast-temperature")?.textContent.trim();

        if (!time || !tempText) {
            return;
        }

        const temp = parseFloat(tempText.replace(/[^\d.-]/g, ""));
        if (Number.isNaN(temp)) {
            return;
        }

        times.push(time);
        temps.push(temp);
    });

    if (times.length === 0 || temps.length === 0) {
        return;
    }

    new Chart(ctx, {
        type: "line",
        data: {
            labels: times,
            datasets: [
                {
                    label: "Temperature (C)",
                    data: temps,
                    borderColor: gradient,
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 3,
                    fill: false,
                },
            ],
        },
        options: {
            plugins: {
                legend: {
                    display: false,
                },
            },
            scales: {
                x: {
                    display: false,
                    grid: {
                        display: false,
                    },
                },
                y: {
                    display: false,
                    grid: {
                        display: false,
                    },
                },
            },
            animation: {
                duration: 750,
            },
        },
    });
});
