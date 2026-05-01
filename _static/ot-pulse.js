/**
 * Directive `<ot-pulse>`
 * Creates dots to pulsate to indicate 'waiting'.
 * by qwiglydee@gmail.com
 *
 * Requires otree-front-2.0, use together with `ot-pulse.css`
 *
 * @example
 * <ot-pulse id="waiting" hidden></ot-pulse>
 *
 * showDisplay("waiting");
 */
class otPulse extends ot.DirectiveBase {
    init() {
        this.elem.innerHTML = "<i></i><i></i><i></i>";
    }
}

ot.attachDirective(otPulse, "ot-pulse");
