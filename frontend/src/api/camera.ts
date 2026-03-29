const API = {
  getCameraFeed: "/camera/whep",
};

export const fetchCameraFeed = async (peerConnection: RTCPeerConnection) => {
  try {
    const response = await fetch(API.getCameraFeed, {
      method: "POST",
      headers: {
        "Content-Type": "application/sdp",
      },
      body: peerConnection.localDescription?.sdp,
    });

    if (!response.ok) {
      throw new Error(
        `WebRTC signaling failed: ${response.status} ${response.statusText}`,
      );
    }

    const answerSdp = await response.text();

    return answerSdp;
  } catch (error) {
    console.error("Error fetching camera feed:", error);
  }
};
