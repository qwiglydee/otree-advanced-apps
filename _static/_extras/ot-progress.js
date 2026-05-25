/**
 * Directive ot-progress
 * Draws progress with two layers with smooth real-time transitions.
 * by qwiglydee@gmail.com
 *
 * Requires otree-front-2.0, use together with `ot-progress.css`
 *
 * All the parameters can be either constants or variable references.
 *
 * @example:
 *    <ot-progress max="..." ticks="..." value="..." value2="..."></ot-progress>
 */
class otProgress extends ot.ContentDirective {
    params = {
        max: {},
        value: { default: 0 },
        value2: {},
        ticks: {},
    };

    render() {
        if (this.elems) return;
        // only render first time
        this.renderBase();
        this.renderTicks();
        this.resetBars();
        if (this.value || this.value2) this.renderBars();
    }

    renderBase() {
        this.elem.classList.add("progress");
        this.elem.innerHTML = `
            <div class="progress-1 progress-bar"></div>
            <div class="progress-2 progress-bar"></div>
            <div class="progress-ticks"></div>
        `;
        // shortcuts to nested elems
        this.elems = {
            bar1: this.elem.querySelector(".progress-1"),
            bar2: this.elem.querySelector(".progress-2"),
            ticks: this.elem.querySelector(".progress-ticks"),
        };
    }

    resetBars() {
        this.elem.setAttribute("reset", ""); // to disable css animation on reset
        this.elems.bar1.style.width = 0;
        this.elems.bar2.style.width = 0;
    }

    renderBars() {
        this.elem.removeAttribute("reset", "");

        if (this.max === undefined || this.value === undefined) return;

        let relative = (val) => ((100 * val) / this.max).toFixed(2) + "%";

        if (this.value !== undefined) {
            this.elems.bar1.style.width = relative(this.value);
        }
        if (this.value !== undefined && this.value2 !== undefined) {
            if (this.value2 === null) {
                this.elems.bar2.style.width = 0;
            } else {
                this.elems.bar2.style.width = relative(this.value2 - this.value);
            }
        }
    }

    renderTicks() {
        this.elems.ticks.innerHTML = "";

        if (this.max === undefined || this.ticks === undefined || this.ticks > this.max) return;

        let num = Math.floor(this.max / this.ticks);

        let relative = (idx) => ((100 * idx) / num).toFixed(2) + "%";

        let ticks = Array.from({ length: num - 1 }).map((e, i) => relative(i + 1));

        this.elems.ticks.innerHTML = ticks.map((p) => `<i style="left: ${p}"></i>`).join("");
    }

    update(updated) {
        if (updated.has("max") || updated.has("ticks")) this.renderTicks();
        if (updated.has("max") || updated.has("value") || updated.has("value2")) {
            if (this.value === null) this.resetBars();
            else this.renderBars();
        }
    }
}

ot.attachDirective(otProgress, "ot-progress");
