// --- DOM Element References ---
const initialView = document.getElementById("initial-view");
const interviewContainer = document.getElementById("interview-container");
const interviewForm = document.getElementById("interviewForm");
const questionEl = document.getElementById("question");
const questionLoading = document.getElementById("question-loading");
const status = document.getElementById("status");
const recordBtn = document.getElementById("recordBtn");
const recordBtnText = document.getElementById("recordBtnText");
const buttonWaveformCanvas = document.getElementById("button-waveform");
const buttonCtx = buttonWaveformCanvas.getContext("2d");
const resultsContainer = document.getElementById("results-container");
const transcriptEl = document.getElementById("transcript");
const feedbackEl = document.getElementById("feedback");
const nextQuestionBtn = document.getElementById("nextQuestionBtn");

// --- State Variables ---
let socket, audioCtx, processor, audioStream, analyser, dataArray, animationId;
let isRecording = false;

// --- Functions ---

async function fetchQuestion() {
  // Show loading indicator
  questionLoading.style.display = "flex";
  questionEl.textContent = "";
  
  const formData = new FormData(interviewForm);
  const response = await fetch("/start-interview", {
    method: "POST",
    body: formData,
  });
  const question = await response.text();
  
  // Hide loading indicator and show question
  questionLoading.style.display = "none";
  questionEl.textContent = question; // Set the new question
  resultsContainer.style.display = "none";
  transcriptEl.innerHTML = "";
  feedbackEl.innerHTML = "";
  status.textContent = "Click the button to start recording.";
  status.classList.add("opacity-10");
  recordBtn.disabled = false;
  recordBtnText.innerHTML = "Start<br />Recording";
  recordBtn.classList.remove("processing-state"); // Ensure processing animation is off
}

function drawWaveforms() {
  const dpr = window.devicePixelRatio || 1;

  // --- Setup Button Waveform ---
  const btnRect = buttonWaveformCanvas.getBoundingClientRect();
  buttonWaveformCanvas.width = btnRect.width * dpr;
  buttonWaveformCanvas.height = btnRect.height * dpr;
  buttonCtx.scale(dpr, dpr);

  function draw() {
    animationId = requestAnimationFrame(draw);
    if (!analyser) return;
    analyser.getByteTimeDomainData(dataArray);

    // --- Draw Button Waveform ---
    buttonCtx.clearRect(0, 0, btnRect.width, btnRect.height);
    buttonCtx.lineWidth = 21;
    buttonCtx.strokeStyle = "#4f46e5";
    buttonCtx.beginPath();
    sliceWidth = btnRect.width / dataArray.length;
    x = 0;
    for (let i = 0; i < dataArray.length; i++) {
      const v = dataArray[i] / 128.0;
      const y = (v * btnRect.height) / 2;
      if (i === 0) buttonCtx.moveTo(x, y);
      else buttonCtx.lineTo(x, y);
      x += sliceWidth;
    }
    buttonCtx.lineTo(btnRect.width, btnRect.height / 2);
    buttonCtx.stroke();
  }
  draw();
}

function floatTo16BitPCM(float32Array) {
  const buffer = new ArrayBuffer(float32Array.length * 2);
  const view = new DataView(buffer);
  for (let i = 0; i < float32Array.length; i++) {
    let s = Math.max(-1, Math.min(1, float32Array[i]));
    view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return new Uint8Array(buffer);
}

async function startRecording() {
  status.classList.remove("opacity-10");
  status.textContent = "Connecting...";
  const jobTitle = document.getElementById("job_title").value;
  const topic = document.getElementById("topic").value;

  socket = new WebSocket(
    `ws://${window.location.host}/ws/audio?question=${encodeURIComponent(questionEl.textContent)}&job_title=${encodeURIComponent(jobTitle)}&topic=${encodeURIComponent(topic)}`,
  );

  socket.onopen = async () => {
    status.textContent = "Requesting microphone...";
    try {
      audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioCtx = new AudioContext({ sampleRate: 16000 });
      const source = audioCtx.createMediaStreamSource(audioStream);
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 2048;
      dataArray = new Uint8Array(analyser.frequencyBinCount);
      source.connect(analyser);

      drawWaveforms();

      processor = audioCtx.createScriptProcessor(4096, 1, 1);
      source.connect(processor);
      processor.connect(audioCtx.destination);
      processor.onaudioprocess = (event) => {
        const input = event.inputBuffer.getChannelData(0);
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(floatTo16BitPCM(input));
        }
      };

      isRecording = true;
      recordBtnText.innerHTML = "Done";
      status.textContent = "Recording...";
    } catch (err) {
      status.textContent = `Mic access failed: ${err.message}`;
    }
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    recordBtn.classList.remove("processing-state"); // Remove processing animation
    status.textContent =
      "Analysis complete. Click 'Retry' to record a new answer or 'Next Question' to continue."; // Update status
    resultsContainer.style.display = "block"; // Show results
    recordBtn.disabled = false; // Re-enable the button
    recordBtnText.innerHTML = "Retry"; // Change button text to "Retry"
    if (data.error) {
      transcriptEl.textContent = data.error;
      return;
    }
    transcriptEl.textContent = data.transcription;
    // Convert markdown feedback to HTML
    console.log("Feedback data:", data.feedback);
    try {
      feedbackEl.innerHTML = marked.parse(data.feedback);
    } catch (error) {
      console.error("Marked parsing error:", error);
      // Fallback to plain text if marked fails
      feedbackEl.textContent = data.feedback;
    }
  };
}

function stopRecording() {
  if (socket && socket.readyState === WebSocket.OPEN) socket.send("stop");
  if (processor) processor.disconnect();
  if (audioCtx) audioCtx.close();
  if (audioStream) audioStream.getTracks().forEach((track) => track.stop());
  if (animationId) cancelAnimationFrame(animationId);

  analyser = null;
  isRecording = false;
  recordBtnText.innerHTML = "Analysing";
  recordBtn.disabled = true;
  status.textContent = "Processing your answer...";
  recordBtn.classList.add("processing-state");
}

// --- Event Listeners ---
interviewForm.onsubmit = async (e) => {
  e.preventDefault();
  initialView.style.display = "none";
  interviewContainer.style.display = "block";
  await fetchQuestion();
};

recordBtn.onclick = () => {
  if (isRecording) {
    stopRecording();
  } else {
    // Check if we're in retry mode (button text is "Retry")
    if (recordBtnText.innerHTML === "Retry") {
      // Clear old answer and feedback
      transcriptEl.innerHTML = "";
      feedbackEl.innerHTML = "";
      resultsContainer.style.display = "none";
      recordBtnText.innerHTML = "Start<br />Recording";
      status.textContent = "Click the button to start recording.";
      status.classList.add("opacity-10");
    }
    startRecording();
  }
};
nextQuestionBtn.onclick = fetchQuestion;
