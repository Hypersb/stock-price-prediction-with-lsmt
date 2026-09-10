import { apiFetch } from "@/lib/api/client";
import type { ModelCatalogResponse } from "@/types/api";

export function listModels() {
  return apiFetch<ModelCatalogResponse>("/models");
}
