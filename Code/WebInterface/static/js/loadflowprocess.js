document.addEventListener('DOMContentLoaded', function () {
  // Step 1: Engine selection
  const engineButtons = document.querySelectorAll('.engine-select-btn');
  const stepEngineInit = document.getElementById('step-engine-init');
  engineButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      stepEngineInit.classList.remove('d-none');
    });
  });

  // Step 2: Continue to Configuration
  const btnInitComplete = document.getElementById('btn-init-complete');
  const stepEngineConfig = document.getElementById('step-engine-config');
  if (btnInitComplete) {
    btnInitComplete.addEventListener('click', function () {
      stepEngineConfig.classList.remove('d-none');
    });
  }

  // Step 3: Continue to Analysis
  const btnConfigComplete = document.getElementById('btn-config-complete');
  const stepRunAnalysis = document.getElementById('step-run-analysis');
  if (btnConfigComplete) {
    btnConfigComplete.addEventListener('click', function () {
      stepRunAnalysis.classList.remove('d-none');
    });
  }

  // Step 4: Run Analysis and Progress Bar
  const btnRunAnalysis = document.getElementById('btn-run-analysis');
  const progressBarContainer = document.getElementById('analysis-progress-bar-container');
  const progressBar = document.getElementById('analysis-progress-bar');
  if (btnRunAnalysis && progressBarContainer && progressBar) {
    btnRunAnalysis.addEventListener('click', function () {
      progressBarContainer.style.display = 'block';
      let progress = 0;
      progressBar.style.width = '0%';
      progressBar.textContent = '0%';
      const interval = setInterval(function () {
        if (progress < 100) {
          progress += 5;
          progressBar.style.width = progress + '%';
          progressBar.textContent = progress + '%';
        } else {
          clearInterval(interval);
          progressBar.textContent = 'Analysis Complete!';
          // Inside the progress bar interval's else block, after progressBar.textContent = 'Analysis Complete!';
          const analysisResults = document.getElementById('analysis-results');
          if (analysisResults) {
            analysisResults.style.display = 'block';
        }
          progressBar.classList.remove('progress-bar-animated');
        }
      }, 200);
    });
  }
});