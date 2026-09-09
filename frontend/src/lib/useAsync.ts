import { useEffect, useState } from "react";

import { apiError } from "./api";

interface AsyncState<T> {
  data?: T;
  error?: string;
  loading: boolean;
}

/** Corre `fn` cuando cambian `deps` y expone {data, error, loading, reload}.
 * `reload()` fuerza una nueva corrida (útil después de una mutación). */
export function useAsync<T>(fn: () => Promise<T>, deps: unknown[]) {
  const [tick, setTick] = useState(0);
  const [state, setState] = useState<AsyncState<T>>({ loading: true });

  useEffect(() => {
    let cancelado = false;
    setState((s) => ({ ...s, loading: true, error: undefined }));
    fn().then(
      (data) => {
        if (!cancelado) setState({ data, loading: false });
      },
      (err) => {
        if (!cancelado) setState({ error: apiError(err), loading: false });
      },
    );
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);

  return { ...state, reload: () => setTick((t) => t + 1) };
}
