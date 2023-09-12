var input_minutes
var input_seconds
var target_timestamp
var timer_milliseconds
var formatted
var timeDifference
var timer_remaining

var totalSeconds
var minutes
var seconds



function checkTime() {
    timeDifference = target_timestamp - Date.now();
    formatted = convertTime(timeDifference);
    document.getElementById("timer_progressbar").value = timeDifference
    document.getElementById('time').innerHTML = '' + formatted;
    
    if (timeDifference <= 0) {
        reset_timer()
        stop_playing()
        my_play_button.innerText = "Start"
        my_play_button.style.backgroundColor = "lightgreen"
    }
}

function convertTime(miliseconds) {
    totalSeconds = Math.floor(miliseconds / 1000);
    minutes = Math.floor(totalSeconds / 60);
    seconds = totalSeconds - minutes * 60;
    return ("00" + minutes).slice(-2) + ':' + ("00" + seconds).slice(-2);
}


function start_pause_timer() {
    if (window.timer) {
        clearInterval(window.timer);
        window.timer = null;
        timer_milliseconds = timeDifference
        document.getElementById('timer_start_pause_button').classList.remove("fa-pause");
        document.getElementById('timer_start_pause_button').classList.add("fa-play");

    } else if (timer_milliseconds){
        target_timestamp = Date.now() + timer_milliseconds;
        window.timer = setInterval(checkTime, 100);
        document.getElementById('timer_start_pause_button').classList.remove("fa-play");
        document.getElementById('timer_start_pause_button').classList.add("fa-pause");

    } else {
        console.log("run")
        input_minutes = document.getElementById('minutes').value;          
        timer_milliseconds = (input_minutes * 60000) + 1000
        target_timestamp = Date.now() + timer_milliseconds;
        window.timer = setInterval(checkTime, 100);
        document.getElementById("timer_progressbar").max = timer_milliseconds
        document.getElementById('timer_start_pause_button').classList.remove("fa-play");
        document.getElementById('timer_start_pause_button').classList.add("fa-pause");               
    }
}

function reset_timer() {
    clearInterval(window.timer);
    window.timer = null;
    timer_milliseconds = null;
    document.getElementById("timer_progressbar").value = document.getElementById("timer_progressbar").max
    document.getElementById('time').innerHTML = convertTime(document.getElementById('minutes').value * 60000)
    document.getElementById('timer_start_pause_button').classList.remove("fa-pause");
    document.getElementById('timer_start_pause_button').classList.add("fa-play");
}