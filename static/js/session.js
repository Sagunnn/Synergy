window.addEventListener('beforeunload', function (e) {
    navigator.sendBeacon('/auto_logout/');
});

var logoutTimer;

    function resetTimer() {
        clearTimeout(logoutTimer);
        logoutTimer = setTimeout(logout, 3600000);  // Set the timer for 1 hour (3600000 ms)
    }

    function logout() {
        window.location.href = "/auto_logout/";  // Redirect to the logout URL
    }

    // Reset the timer on these events
    window.onload = resetTimer;
    document.onmousemove = resetTimer;
    document.onkeypress = resetTimer;
    document.ontouchstart = resetTimer;