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
 * onUpdate('vars.name', function updateVar(var_value) { ... })
 * onUpdate('vars.objname.fieldname', function updateField(field_value) { ... })
 * onUpdate('vars.objname.*', function updateObj(obj_value) { ... })
 */

function onUpdate(varname, handler) {
    if (!varname.startsWith("vars.")) throw Error("onUpdate: invalid var name, expecting `vars.` ");
    let varref = varname.slice(5);
    ot.onEvent(
        "update",
        (e) => e.detail.changes.affect(varref),
        (e) => handler(e.detail.changes.extract(varref)),
    );
}

/** switching directives */

class otDisplay extends ot.ContentDirective {
    params = { val: { attr: "ot-display", default: false } };

    render() {
        let toggle = ot.isVoid(this.val) || this.val == false;
        this.elem.toggleAttribute("hidden", toggle);
        autofocus(this.elem);
    }
}
ot.attachDirective(otDisplay, "[ot-display]");

class otVisible extends ot.ContentDirective {
    params = { val: { attr: "ot-visible", default: false } };

    render() {
        let toggle = ot.isVoid(this.val) || this.val == false;
        this.elem.toggleAttribute("invisible", toggle);
        this.elem.style.visibility = toggle ? "hidden" : null;
        autofocus(this.elem);
    }
}
ot.attachDirective(otVisible, "[ot-visible]");

class otEnable extends ot.ContentDirective {
    params = { val: { attr: "ot-enable", default: false } };

    render() {
        let toggle = ot.isVoid(this.val) || this.val == false;
        this.elem.toggleAttribute("disabled", toggle);
        autofocus(this.elem);
    }
}
ot.attachDirective(otEnable, "[ot-enable]");

class otRequired extends ot.ContentDirective {
    params = { val: { attr: "ot-required", default: false } };

    render() {
        let toggle = ot.isVoid(this.val) || this.val == false;
        this.elem.toggleAttribute("required", !toggle);
    }
}
ot.attachDirective(otRequired, "[ot-required]");

function autofocus(elem) {
    if (elem.hasAttribute("hidden") || elem.hasAttribute("invisible") || elem.hasAttribute("disabled")) return;

    if (elem.hasAttribute("autofocus")) {
        // refocus when re-enabled
        elem.focus();
    } else {
        // nested inputs of re-displayed block
        let nested = elem.querySelector("[autofocus]:not([disabled]):not([hidden]):not([invisible])");
        if (nested) nested.focus();
    }
}
