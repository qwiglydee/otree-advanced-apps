/**
 * Some enhancements for otree-front
 * by qwiglydee@gmail.com
 */

/**
 * Helpers for lifecycle handlers.
 *
 * @example
 * onLoad(function startGame() { ... });
 * onSubmit(function submitPage() { ... });
 */
function onLoad(handler) {
    ot.onEvent("loaded", handler);
}
function onSubmit(handler) {
    ot.onEvent("submitted", handler);
}

/**
 * Helpers for input handler.
 *
 * @example
 * onInput('inputname', function inputSomething(value) { ... });
 * onInputs(function inputAll(name, value) { ... });
 */
function onInputs(handler) {
    ot.onEvent("input", (e) => handler(e.detail.name, e.detail.value));
}
function onInput(name, handler) {
    ot.onEvent("input", name, (e) => handler(e.detail.value));
}

/**
 * Helpers for timer handlers.
 *
 * @example
 * onTimer('timername', function handleTimer(elapsed, counter) { ... });
 * onTimers(function handleTimers(name, elapsed, counter) { ... });
 */
function onTimers(handler) {
    ot.onEvent("timer", (e) => handler(e.detail.name, e.detail.elapsed, e.detail.count));
}
function onTimer(name, handler) {
    ot.onEvent("timer", name, (e) => handler(e.detail.elapsed, e.detail.count));
}

/**
 * Helper for built-in oTree page timer.
 *
 * @example
 * onCountdown(function handleCountdown(remaining_seconds) { ... });
 */
function onCountdown(handler) {
    ot.onEvent("countdown", (e) => handler(e.detail.remaining));
}

if (document.querySelector(".otree-timer")) {
    $(".otree-timer__time-left").on("update.countdown", function (e) {
        ot.triggerEvent("countdown", { remaining: e.offset.totalSeconds });
    });
}
/**
 * Helper for built-in oTree update event.
 *
 * @example
 * onUpdate('varname', function updateVar(var_value) { ... })
 * onUpdate('objname.fieldname', function updateField(field_value) { ... })
 * onUpdate('objname.*', function updateObj(obj_value) { ... })
 */

function onUpdate(varname, handler) {
    ot.onEvent(
        "update",
        (e) => e.detail.changes.affect(varname),
        (e) => handler(e.detail.changes.extract(varname)),
    );
}
