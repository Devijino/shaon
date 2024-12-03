function updateClocks() {
    const now = new Date();

    // הדפסת זמני הזריחה והשקיעה לבדיקה
    console.log("Now (Client Time):", now.toISOString());
    console.log("Sunrise:", sunrise.toISOString());
    console.log("Sunset:", sunset.toISOString());

    // עדכון שעון רגיל
    document.getElementById('regularTime').innerText = now.toLocaleTimeString('he-IL');
    document.getElementById('regularDate').innerText = now.toLocaleDateString('he-IL');

    // חישוב שעות זמניות
    let temporaryHours = "--";
    let temporaryMinutes = "--";

    if (now >= sunrise && now <= sunset) {
        const dayLength = (sunset - sunrise) / 12; // אורך שעה זמנית במילישניות
        const elapsed = now - sunrise;
        temporaryHours = Math.floor(elapsed / dayLength) + 1;
        temporaryMinutes = Math.floor((elapsed % dayLength) / (dayLength / 60));

        console.log("Temporary Hours:", temporaryHours);
        console.log("Temporary Minutes:", temporaryMinutes);
    } else {
        console.log("It's nighttime.");
    }

    // עדכון שעון זמניות
    if (temporaryHours === "--") {
        document.getElementById('hebrewTime').innerText = "--:--";
    } else {
        document.getElementById('hebrewTime').innerText = `${temporaryHours}:${String(temporaryMinutes).padStart(2, '0')}`;
    }

    // שינוי צבע הרקע בהתאם לזמן היום והלילה
    const regularClock = document.getElementById('regularClock');
    const hebrewClock = document.getElementById('hebrewClock');

    if (now >= sunrise && now <= sunset) {
        // יום
        regularClock.classList.add('daytime');
        regularClock.classList.remove('nighttime');
        hebrewClock.classList.add('daytime');
        hebrewClock.classList.remove('nighttime');
    } else {
        // לילה
        regularClock.classList.add('nighttime');
        regularClock.classList.remove('daytime');
        hebrewClock.classList.add('nighttime');
        hebrewClock.classList.remove('daytime');
    }
}

setInterval(updateClocks, 1000);
updateClocks();
