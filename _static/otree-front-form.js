/**
 * Registering all otree-front inputs directives on standard form inputs
 */

window.addEventListener("DOMContentLoaded", function () {
    ot.attachDirective(ot.otTextInput, "input:is([type=text],[type=number])");
    ot.attachDirective(ot.otRangeInput, "input[type=range]");
    ot.attachDirective(ot.otRadioInput, "input[type=radio]");
    ot.attachDirective(ot.otCheckInput, "input[type=checkbox]");
    ot.attachDirective(ot.otInput, "input:not([type=text],[type=number],[type=range],[type=radio],[type=checkbox])");
    ot.attachDirective(ot.otTextInput, "textarea");
    ot.attachDirective(ot.otInput, "select");
});
