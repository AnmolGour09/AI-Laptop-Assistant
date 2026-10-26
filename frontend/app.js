const activityList = document.querySelector("#activity-list");
const activityEmpty = document.querySelector(".activity-empty");
const toast = document.querySelector("#toast");
const micButton = document.querySelector("#mic-button");
const micButtonLabel = document.querySelector("#mic-button-label");
const dialogBackdrop = document.querySelector("#dialog-backdrop");
const connectButton = document.querySelector("#connect-button");
const connectLabel = document.querySelector("#connect-label");
const sessionBadgeLabel = document.querySelector("#session-badge-label");
const commandFootnote = document.querySelector("#command-footnote");
let toastTimer;
let room = null;
let isConnecting = false;
let microphoneEnabled = false;
let microphoneBusy = false;
let pendingMicrophoneState = null;
let introComplete = false;
let taskActive = false;
let taskStartedAt = 0;
let taskMuteTimer = null;
let taskTimeoutTimer = null;
let autoMutedForTask = false;

const TASK_MUTE_DELAY_MS = 3000;
const TASK_TIMEOUT_MS = 90000;

function updateClock() {
  const now = new Date();
  const clock = document.querySelector("#clock");
  const dateLabel = document.querySelector("#today-label");
  clock.innerHTML = `${new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  }).format(now).replace(/\s?(AM|PM)$/i, "<span> $1</span>")}`;
  dateLabel.textContent = new Intl.DateTimeFormat(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
  }).format(now).toUpperCase();
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("visible"), 3800);
}

function addActivity(text, speaker) {
  const entry = document.createElement("div");
  const time = document.createElement("time");
  entry.className = "activity-entry";
  entry.append(document.createTextNode(`${speaker}: ${text}`));
  time.textContent = new Intl.DateTimeFormat(undefined, {
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date());
  entry.append(time);
  activityList.prepend(entry);
  activityEmpty.hidden = true;
}

function setConnectionState(state) {
  const connected = state === "connected";
  document.querySelector(".topbar").classList.toggle("session-connected", connected);
  document.querySelector(".topbar").classList.toggle("session-connecting", state === "connecting");
  connectButton.disabled = state === "connecting";
  connectLabel.textContent = connected ? "Disconnect" : state === "connecting" ? "Connecting…" : "Connect";
  sessionBadgeLabel.textContent = connected ? "LIVE SESSION" : state === "connecting" ? "CONNECTING" : "READY TO CONNECT";
  commandFootnote.lastChild.textContent = connected
    ? " Speak to Jarvis and use the button to mute or unmute your microphone."
    : " Connect to Jarvis, then use the microphone button to mute or unmute.";
  updateMicrophoneControl();
}

function updateMicrophoneControl() {
  const canToggle = Boolean(room) && introComplete && !taskActive && !microphoneBusy;
  micButton.disabled = !canToggle;
  micButton.classList.toggle("muted", Boolean(room) && !microphoneEnabled);
  micButtonLabel.textContent = !room
    ? "Connect to enable microphone"
    : !introComplete
      ? "Microphone muted · Jarvis is introducing"
      : taskActive
        ? microphoneEnabled
          ? "Task received · microphone mutes in 3 seconds"
          : "Jarvis is working · microphone muted"
        : microphoneEnabled
          ? "Mute microphone"
          : "Unmute microphone";
  micButton.setAttribute("aria-label", micButtonLabel.textContent);
  micButton.setAttribute("aria-pressed", String(microphoneEnabled));
  micButton.title = micButtonLabel.textContent;
  sessionBadgeLabel.textContent = !room
    ? "READY TO CONNECT"
    : !introComplete
      ? "INTRODUCING"
      : taskActive
        ? "WORKING"
        : microphoneEnabled
          ? "LISTENING"
          : "MICROPHONE MUTED";
  commandFootnote.lastChild.textContent = !room
    ? " Connect to Jarvis to start. The microphone will stay muted during its introduction."
    : !introComplete
      ? " Microphone is muted while Jarvis gives its introduction."
      : taskActive
        ? microphoneEnabled
          ? " Task received. Microphone will mute after 3 seconds while Jarvis works."
          : " Jarvis is working. Microphone is muted and will turn on when the task is complete."
        : microphoneEnabled
          ? " Jarvis is listening. Use the button to mute or unmute."
          : " Microphone is muted. Use the button to unmute.";
}

function clearTaskTimers() {
  clearTimeout(taskMuteTimer);
  clearTimeout(taskTimeoutTimer);
  taskMuteTimer = null;
  taskTimeoutTimer = null;
}

async function setMicrophoneEnabled(enabled) {
  if (!room) {
    pendingMicrophoneState = enabled;
    return;
  }
  if (microphoneBusy) {
    pendingMicrophoneState = enabled;
    return;
  }
  if (microphoneEnabled === enabled) return;
  microphoneBusy = true;
  updateMicrophoneControl();
  try {
    await room.localParticipant.setMicrophoneEnabled(enabled);
    microphoneEnabled = enabled;
  } catch (error) {
    showConnectionError(error);
    if (!enabled && taskActive) {
      taskActive = false;
      autoMutedForTask = false;
      clearTaskTimers();
    }
  } finally {
    microphoneBusy = false;
    updateMicrophoneControl();
    if (pendingMicrophoneState !== null && room) {
      const nextState = pendingMicrophoneState;
      pendingMicrophoneState = null;
      if (microphoneEnabled !== nextState) {
        setMicrophoneEnabled(nextState);
      }
    }
  }
}

function finishTask() {
  clearTaskTimers();
  taskActive = false;
  taskStartedAt = 0;
  const shouldUnmute = autoMutedForTask;
  autoMutedForTask = false;
  updateMicrophoneControl();
  if (shouldUnmute) {
    setMicrophoneEnabled(true);
  }
}

function scheduleTaskMute() {
  clearTimeout(taskMuteTimer);
  const remaining = Math.max(0, TASK_MUTE_DELAY_MS - (Date.now() - taskStartedAt));
  taskMuteTimer = setTimeout(() => {
    if (room && taskActive && microphoneEnabled) {
      autoMutedForTask = true;
      setMicrophoneEnabled(false);
    }
  }, remaining);
}

function handleVoiceStatus(status) {
  if (status === "intro_complete") {
    introComplete = true;
    updateMicrophoneControl();
    setMicrophoneEnabled(true);
    showToast("Jarvis is ready and listening.");
    return;
  }

  if (status === "intro_failed") {
    introComplete = true;
    updateMicrophoneControl();
    setMicrophoneEnabled(true);
    showToast("Jarvis could not speak its introduction. The microphone is enabled; try speaking.");
    return;
  }

  if (!introComplete) return;

  if (status === "task_received") {
    taskActive = true;
    taskStartedAt = Date.now();
    autoMutedForTask = false;
    clearTaskTimers();
    scheduleTaskMute();
    taskTimeoutTimer = setTimeout(() => {
      if (!taskActive) return;
      showToast("Jarvis is taking longer than expected. Microphone is available again.");
      finishTask();
    }, TASK_TIMEOUT_MS);
    updateMicrophoneControl();
    return;
  }

  if (status === "task_processing") {
    if (!taskActive) {
      taskActive = true;
      taskStartedAt = Date.now();
      taskTimeoutTimer = setTimeout(() => {
        if (!taskActive) return;
        showToast("Jarvis is taking longer than expected. Microphone is available again.");
        finishTask();
      }, TASK_TIMEOUT_MS);
    }
    scheduleTaskMute();
    updateMicrophoneControl();
    return;
  }

  if (status === "task_complete" && taskActive) {
    finishTask();
  }
}

function showConnectionError(error) {
  const message = error instanceof Error ? error.message : "An unexpected connection error occurred.";
  showToast(`Could not connect to Jarvis: ${message}`);
}

async function connectAssistant() {
  if (isConnecting || room) return;
  if (window.location.protocol === "file:") {
    showToast("This is a standalone preview. Start Jarvis with .\\run.bat, then open http://127.0.0.1:8000/.");
    return;
  }
  isConnecting = true;
  setConnectionState("connecting");
  let newRoom;
  try {
    const { Room, RoomEvent, Track } = await import(
      "https://cdn.jsdelivr.net/npm/livekit-client@2.15.6/+esm"
    );
    const response = await fetch("/api/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    });
    const credentials = await response.json();
    if (!response.ok) {
      throw new Error(credentials.error || `Token request failed (${response.status}).`);
    }

    newRoom = new Room({
      adaptiveStream: true,
      dynacast: true,
      audioCaptureDefaults: {
        autoGainControl: true,
        echoCancellation: true,
        noiseSuppression: true,
      },
    });
    newRoom.on(RoomEvent.TrackSubscribed, (track) => {
      if (track.kind !== Track.Kind.Audio) return;
      const audio = track.attach();
      audio.autoplay = true;
      audio.setAttribute("playsinline", "");
      audio.dataset.jarvisAudio = "";
      document.body.append(audio);
      audio.play().catch(() => showToast("Click the page once to allow Jarvis audio playback."));
    });
    newRoom.on(RoomEvent.TrackUnsubscribed, (track) => {
      track.detach().forEach((element) => element.remove());
    });
    newRoom.on(RoomEvent.Disconnected, () => {
      if (room !== newRoom) return;
      room = null;
      microphoneEnabled = false;
      introComplete = false;
      taskActive = false;
      autoMutedForTask = false;
      pendingMicrophoneState = null;
      clearTaskTimers();
      updateMicrophoneControl();
      document.querySelectorAll("[data-jarvis-audio]").forEach((audio) => audio.remove());
      setConnectionState("disconnected");
      showToast("Jarvis session disconnected.");
    });
    newRoom.registerTextStreamHandler("lk.transcription", async (reader, participantIdentity) => {
      const text = (await reader.readAll()).trim();
      if (text) {
        addActivity(
          text,
          participantIdentity === newRoom.localParticipant.identity ? "You" : "Jarvis",
        );
      }
    });
    newRoom.registerTextStreamHandler("jarvis.voice", async (reader) => {
      try {
        const message = JSON.parse((await reader.readAll()).trim());
        handleVoiceStatus(message.status);
      } catch (error) {
        console.error("Could not read Jarvis voice status.", error);
      }
    });

    introComplete = false;
    taskActive = false;
    autoMutedForTask = false;
    microphoneEnabled = false;
    pendingMicrophoneState = null;
    await newRoom.connect(credentials.url, credentials.token);
    room = newRoom;
    setConnectionState("connected");
    await setMicrophoneEnabled(introComplete);
    showToast("Connected. Microphone stays muted during Jarvis's introduction.");
  } catch (error) {
    if (newRoom) await newRoom.disconnect().catch(() => {});
    setConnectionState("disconnected");
    showConnectionError(error);
  } finally {
    isConnecting = false;
  }
}

async function disconnectAssistant() {
  const currentRoom = room;
  room = null;
  microphoneEnabled = false;
  introComplete = false;
  taskActive = false;
  autoMutedForTask = false;
  pendingMicrophoneState = null;
  clearTaskTimers();
  updateMicrophoneControl();
  setConnectionState("disconnected");
  if (currentRoom) await currentRoom.disconnect();
  document.querySelectorAll("[data-jarvis-audio]").forEach((audio) => audio.remove());
}

connectButton.addEventListener("click", () => {
  if (room) {
    disconnectAssistant().catch(showConnectionError);
  } else {
    connectAssistant();
  }
});

document.querySelector("#help-button").addEventListener("click", () => {
  dialogBackdrop.hidden = false;
  document.querySelector("#dialog-close").focus();
});

function closeDialog() {
  dialogBackdrop.hidden = true;
  document.querySelector("#help-button").focus();
}

document.querySelector("#dialog-close").addEventListener("click", closeDialog);
document.querySelector("#dialog-action").addEventListener("click", closeDialog);
dialogBackdrop.addEventListener("click", (event) => {
  if (event.target === dialogBackdrop) closeDialog();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !dialogBackdrop.hidden) closeDialog();
});

document.querySelector("#all-capabilities").addEventListener("click", (event) => {
  event.preventDefault();
  showToast("These capabilities reflect tools available in the Jarvis Python agent.");
});

document.querySelector("#activity-more").addEventListener("click", () => {
  showToast("Activity shown here is stored only in this page preview.");
});

document.querySelector(".profile-button").addEventListener("click", () => {
  showToast("Personal workspace · Anmol Gour");
});

const navigationLinks = [...document.querySelectorAll(".nav-link")];
function updateNavigation() {
  const currentHash = window.location.hash || "#dashboard";
  navigationLinks.forEach((link) => {
    link.classList.toggle("active", link.hash === currentHash);
  });
}
window.addEventListener("hashchange", updateNavigation);
updateNavigation();

micButton.addEventListener("click", async () => {
  if (!room || !introComplete || taskActive || microphoneBusy) return;
  await setMicrophoneEnabled(!microphoneEnabled);
  showToast(microphoneEnabled ? "Microphone on." : "Microphone muted.");
});

updateClock();
updateMicrophoneControl();
setInterval(updateClock, 30_000);
