import { formatTimestamp } from "../utils/time";

const API = {
  getDeviceTelemetry:
    "/api/v1/event/latest_by_type?event_type=DEVICE_TELEMETRY",
};

export type DeviceHealthPayload = {
  cpu: string;
  ram: string;
  temperature: string;
  voltage: string;
  camera_connected: boolean;
  camera_view_status: any;
  is_online: boolean;
  timestamp: string;
};

export const fetchDeviceHealth = async () => {
  try {
    const response = await fetch(API.getDeviceTelemetry);

    if (response.ok) {
      const data = await response.json();
      const { payload } = data;

      return { ...payload, timestamp: formatTimestamp(data.timestamp) };
    }
  } catch (error) {
    console.error("Error fetching device health:", error);
  }
};
