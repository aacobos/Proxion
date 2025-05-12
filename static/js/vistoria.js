let currentStep = 1;

function showStep(step) {
    document.querySelectorAll('.step').forEach(el => el.classList.remove('active'));
    document.querySelector(`#step${step}`).classList.add('active');

    document.querySelectorAll('.progress-step').forEach(el => el.classList.remove('active'));
    document.querySelector(`#step${step}-progress`).classList.add('active');

    currentStep = step;
}

function nextStep(current) {
    if (current < 4) {
        showStep(current + 1);
    }
}

function prevStep(current) {
    if (current > 1) {
        showStep(current - 1);
    }
}
