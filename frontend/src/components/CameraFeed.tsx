import { useRef, useState, useEffect } from "react";

import { fetchCameraFeed } from "../api/camera";

export function CameraFeed({ maxWidth = "" }) {
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
    <>
      <video
        ref={videoRef}
        id="v"
        autoPlay
        playsInline
        muted
        style={{
          width: "100%",
          background: "black",
          maxWidth,
          display: isLoading ? "none" : "block",
        }}
        data-webrtc-url=""
      ></video>
      {isLoading && (
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-black/30 border-t-black" />
      )}

      {streamError ? (
        <p className="mt-2 text-sm text-red-600">{streamError}</p>
      ) : null}
    </>
  );
}
