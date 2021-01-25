var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

function renderCalendar(d) {
    try {
        document.querySelector("#cal").innerHTML = "";
    } catch {
        let el = document.createElement("div");
        el.id = "cal";
        document.querySelector("main").appendChild(el);
    }

    let date = new Date(d);

    let headingEl = document.querySelector("h1");
    headingEl.innerHTML = months[date.getMonth()];

    let yearEl = document.querySelector("h2");
    yearEl.innerHTML = date.getFullYear();

    let calendar = calendarize(d);
    let calendarEl = document.querySelector("#cal");

    let days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    for (let d of days) {
        let label = document.createElement("div");
        label.className = "dayLabel";
        label.innerText = d;
        calendarEl.appendChild(label);
    }

    for (let i in calendar) {
        let week = calendar[i];
        for (let day of week) {
            let el = document.createElement("div");
            el.className = i == calendar.length - 1 ? "last-week day" : "day";
            el.innerHTML = day != 0 ? day : "&nbsp;";
            calendarEl.appendChild(el);
        }
    }
}

document.querySelector("#start").onchange = (e) => {
    renderCalendar(e.target.value);
}

renderCalendar("2021-01-01");