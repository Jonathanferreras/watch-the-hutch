import { useRef, useState, useEffect } from "react";

import { fetchCameraFeed } from "../api/camera";

export function CameraFeed() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const [streamError, setStreamError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const videoEl = videoRef.current;

    if (!videoEl) {
      return;
    }

    const createPeerConnection = () =>
      new RTCPeerConnection({ iceServers: [] });

    const waitForIceGatheringComplete = async (pc: RTCPeerConnection) => {
      if (pc.iceGatheringState === "complete") {
        return;
      }

      await new Promise<void>((resolve) => {
        const checkState = () => {
          if (pc.iceGatheringState === "complete") {
            pc.removeEventListener("icegatheringstatechange", checkState);
            resolve();
          }
        };

        pc.addEventListener("icegatheringstatechange", checkState);
      });
    };

    const startWebRtc = async () => {
      setStreamError("");
      setIsLoading(true);

      const inbound = new MediaStream();
      const pc = createPeerConnection();

      peerConnectionRef.current = pc;
      videoEl.srcObject = inbound;
      pc.addTransceiver("video", { direction: "recvonly" });

      pc.ontrack = async (event) => {
        inbound.addTrack(event.track);

        try {
          await videoEl.play();
          setIsLoading(false);
        } catch (error) {
          console.warn("Video playback was blocked:", error);
        }
      };

      pc.onconnectionstatechange = () => {
        if (pc.connectionState === "failed") {
          setStreamError("Video connection failed.");
        }
      };

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      await waitForIceGatheringComplete(pc);

      const answerSdp = await fetchCameraFeed(pc);
      await pc.setRemoteDescription({ type: "answer", sdp: answerSdp });
    };

    startWebRtc().catch((error) => {
      console.error("Error starting WebRTC stream:", error);
      setStreamError(
        error instanceof Error ? error.message : "Unable to start video feed.",
      );
    });

    return () => {
      peerConnectionRef.current?.close();
      peerConnectionRef.current = null;
      videoEl.srcObject = null;
    };
  }, []);

  return (
    <section className="rounded-2xl border border-slate-200 bg-slate-50 p-3">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div>
          <p className="text-[11px] uppercase tracking-[0.24em] text-slate-400">
            Camera feed
          </p>
          <p className="text-sm font-semibold text-slate-800">Live view</p>
        </div>
        <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs text-slate-500">
          WebRTC
        </span>
      </div>

      <div className="relative overflow-hidden rounded-xl border border-slate-200 bg-slate-900">
        <video
          ref={videoRef}
          id="v"
          autoPlay
          playsInline
          muted
          style={{
            width: "100%",
            display: isLoading ? "none" : "block",
          }}
          data-webrtc-url=""
        ></video>

        {isLoading && (
          <div className="flex aspect-video items-center justify-center bg-slate-100">
            <div className="flex items-center gap-3 text-sm text-slate-500">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-slate-300 border-t-slate-700" />
              Connecting stream...
            </div>
          </div>
        )}
      </div>

      {streamError ? (
        <p className="mt-2 text-sm text-red-600">{streamError}</p>
      ) : null}
    </section>
  );
}
