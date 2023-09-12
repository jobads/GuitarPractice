"use strict"

var AudioContext = window.AudioContext || window.webkitAudioContext; // cross browser    
var audio_context
var oscillator
var gain

var my_play_button
var my_bpm_input_range
var my_volume_input = 5

var my_tap_results

var char_to_increment = {}

var prev_tap_time = 0
var number_of_taps = 0
var accumulated_tap_time = 0

var beats = "1"
var current_beat = 1

var running = false


var sidebar
var sidebarTrigger




function my_onload() {

    my_play_button = document.getElementById("my_play_button")
    my_bpm_input_range = document.getElementById("my_bpm_input_range")
    sidebar = document.getElementById("sidebar")
    sidebarTrigger = document.getElementById("sidebar__trigger")
}

function play_or_stop() {

    // can't do this in onload because browser wants an explicit user gesture
    if (audio_context == null) {
        audio_context = new AudioContext()

        // There's a "node graph"  oscillator->gain->destination
        oscillator = audio_context.createOscillator()
        oscillator.type = "sine"
        oscillator.frequency.value = 1000
        gain = audio_context.createGain()
        gain.gain.value = 0
        oscillator.connect(gain)
        gain.connect(audio_context.destination)
        oscillator.start()
    }

    if (my_play_button.innerText == "Start") {
        play()
        // toggle text
        my_play_button.innerText = "Stop"
        my_play_button.style.backgroundColor = "red"
    } else {
        stop_playing()
        // toggle text
        my_play_button.innerText = "Start"
        my_play_button.style.backgroundColor = "lightgreen"
    }
}

function stop_start() {
    current_beat = 1
    if (running) {
        stop_playing()
        play()
    }
}

function play() {

    running = true

    var volume

    var now = audio_context.currentTime

    // schedule click 1 a little in the future so that click 2 doesn't come right after the late click 1
    now += .5

    // Schedule 15 minutes of iterations
    // This seem to go bad if I schedule TOO many (race condition?)
    // I couldn't figure out a way to do this where the metronome would never run out. 
    var iterations = 15 * my_bpm_input_range.value

    // how much time from one click to the next
    var interval_in_seconds = 60.0 / my_bpm_input_range.value

    for (var i = 0; i < iterations; i++) {
        // calc how loud, calc if this beat should be the louder "accented" beat
        volume = 0.5
        schedule_one_click(now + (i * interval_in_seconds), volume)
    }

}

function stop_playing() {
    running = false
    var time = audio_context.currentTime
    gain.gain.cancelScheduledValues(time)
    gain.gain.setValueAtTime(0, time)
}

function schedule_one_click(time, volume) {
    gain.gain.cancelScheduledValues(time)
    gain.gain.setValueAtTime(0, time)
    gain.gain.linearRampToValueAtTime(volume, time + .001);
    gain.gain.linearRampToValueAtTime(0, time + .001 + .01);
}



function change_frequency(el) {
    oscillator.frequency.value = el.value
    stop_start()
}

function change_bpm() {
    stop_start()
}

function change_bpm_range() {
    document.getElementById("input_bpm").value = document.getElementById("my_bpm_input_range").value;
    stop_start()
}

function change_beats(el) {
    beats = el.value
    stop_start()
}

function increment_bpm(increment) {
    // put focus back to play/stop otherwise spacebar affects last pressed button
    //my_play_button.focus()
    my_bpm_input_range.value = parseInt(my_bpm_input_range.value) + increment
    change_bpm_range()
    // so that the spacebar keeps working
    my_play_button.focus()
}

function sidebar_hide_show() {
    if (sidebar.classList.contains('isOpened')) {
        sidebar.classList.remove('isOpened');
        sidebarTrigger.classList.remove("fa-circle-chevron-left");
        sidebarTrigger.classList.add("fa-circle-chevron-right");
    } else {
        sidebar.classList.add('isOpened');
        sidebarTrigger.classList.remove("fa-circle-chevron-right");
        sidebarTrigger.classList.add("fa-circle-chevron-left");
    }        
}

