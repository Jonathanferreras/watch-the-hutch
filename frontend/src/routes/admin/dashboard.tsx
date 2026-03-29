import { useEffect, useRef, useState } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";

import { logoutUser, requireUser } from "../../api/auth";
import { fetchCameraFeed } from "../../api/camera";

export const Route = createFileRoute("/admin/dashboard")({
  component: AdminDashboardComponent,
  loader: () => requireUser(),
});

function AdminDashboardComponent() {
  const navigate = useNavigate();
  const currentUser = Route.useLoaderData();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const [streamError, setStreamError] = useState("");

  const handleLogout = async () => {
    peerConnectionRef.current?.close();
    peerConnectionRef.current = null;
    await logoutUser();
    await navigate({ to: "/admin" });
  };

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

      const inbound = new MediaStream();
      const pc = createPeerConnection();

      peerConnectionRef.current = pc;
      videoEl.srcObject = inbound;
      pc.addTransceiver("video", { direction: "recvonly" });

      pc.ontrack = async (event) => {
        inbound.addTrack(event.track);

        try {
          await videoEl.play();
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
    <div className="p-4">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold">Admin Dashboard</h3>
          <p className="text-sm">
            Logged in as {currentUser.username} ({currentUser.role})
          </p>
        </div>
        <button className="rounded border px-3 py-2" onClick={handleLogout}>
          Logout
        </button>
      </div>
      <div>
        <h2>Camera Feed</h2>
        <video
          ref={videoRef}
          id="v"
          autoPlay
          playsInline
          muted
          style={{ width: "100%", background: "black" }}
          data-webrtc-url=""
        ></video>
        {streamError ? (
          <p className="mt-2 text-sm text-red-600">{streamError}</p>
        ) : null}
      </div>
    </div>
  );
}
