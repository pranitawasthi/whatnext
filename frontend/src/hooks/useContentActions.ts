import { useState } from "react";
import { api } from "../lib/api";
import type { InteractionStatus } from "../types/api";

export function useContentActions() {
  const [message, setMessage] = useState("");

  async function log(contentId: string, rating: number | null, status: InteractionStatus) {
    setMessage("");
    await api.upsertInteraction(contentId, rating, status);
    setMessage("Saved to your profile");
    window.setTimeout(() => setMessage(""), 1800);
  }

  return { log, message };
}
