import { Customer } from "./lib";
export type Comparison = {
  validation: Record<string, number>;
  test: Record<string, number>;
  training_seconds: number;
};
export type Model = {
  selected: string;
  version: string;
  threshold: number;
  trained_at: string;
  comparison: Record<string, Comparison>;
  dataset: { splits: Record<string, { rows: number }>; churn_rate: number };
  regression: { mae: number; rmse: number; r2: number };
  selection_policy: string;
  training_seconds: number;
};
export type Dashboard = {
  total_predictions: number;
  high_risk: number;
  average_probability: number | null;
  value_at_risk: number;
  recent: Customer[];
  distribution: { range: string; count: number }[];
};
export type Monitor = {
  status: string;
  rows: number;
  features: Record<
    string,
    {
      psi: number;
      missing_rate: number;
      out_of_range_rate: number;
      drift: boolean;
    }
  >;
  performance: { status: string; rows: number; f1?: number; roc_auc?: number };
};
export type Explanation = {
  prediction: { churn_probability: number };
  base_probability: number;
  explanation: { feature: string; contribution: number; value: number }[];
  explanation_note: string;
};
