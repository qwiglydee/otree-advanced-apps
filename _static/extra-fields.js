function updateSliderOutput(slider) {
    let output = document.querySelector(`output[for=${slider.id}]`);
    output.textContent = slider.value;
    const val = Number(slider.value),
        min = Number(slider.min),
        max = Number(slider.max);
    let offset = (val - min) / (max - min);
    output.style.left = `${offset * 100}%`;
}
window.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[type=range]").forEach((elem) => updateSliderOutput(elem));
});
