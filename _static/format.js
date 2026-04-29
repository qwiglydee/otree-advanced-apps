/**
 * Format number with precision and sign
 * @param {*} value
 * @param {*} format: ".2" "+.2"
 */
const FORMAT_RE = /(\+?)\.(\d+)/;
function format_number(value, format) {
    let [_, sgn, prc] = format.match(FORMAT_RE);
    return (sgn == "+" && value > 0 ? "+" : "") + value.toFixed(prc);
}
