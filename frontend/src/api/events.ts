const API = {
  getDeviceTelemetry:
    "/api/v1/event/latest_by_type?event_type=DEVICE_TELEMETRY",
};

export type DeviceHealthResponse = {
  event_id: string;
  source_id: string;
  source_type: string;
  payload: DeviceHealthPayload;
  payloadType: string;
  timestamp: string;
};

export type DeviceHealthPayload = {
  cpu: string;
  ram: string;
  temperature: string;
  voltage: string;
  camera_connected: boolean;
  camera_view_status: any;
  is_online: boolean;
};

export const fetchDeviceHealth = async () => {
  try {
    const response = await fetch(API.getDeviceTelemetry);

    if (response.ok) {
      const data: DeviceHealthResponse = await response.json();
      const { cpu, ram, temperature, voltage, camera_connected, is_online } =
        data.payload;

      return {
        cpu,
        ram,
        temperature,
        voltage,
        cameraConnected: camera_connected,
        isOnline: is_online,
        timestamp: data.timestamp,
      };
    }
  } catch (error) {
    console.error("Error fetching device health:", error);
  }
};
