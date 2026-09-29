export type Customer = { id:number; customer_id:string; probability:number; risk:string; value_at_risk:number; timestamp:string; features:Record<string, number|string|null>; model_version:string };
export const percent = (n:number) => `${(n*100).toFixed(1)}%`;
export async function api<T>(path:string, body?:unknown):Promise<T> {
  const response = await fetch(`/api${path}`, {method:body?'POST':'GET',headers:{'Content-Type':'application/json', ...(sessionStorage.getItem('apiKey') ? {'X-API-Key':sessionStorage.getItem('apiKey')!}: {})},body:body?JSON.stringify(body):undefined});
  if (!response.ok) throw new Error(`Request failed (${response.status}). ${await response.text()}`);
  return response.json();
}
