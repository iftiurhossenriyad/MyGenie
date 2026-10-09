import { isAxiosError } from 'axios';
import type { ApiError } from '../types';

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (!isAxiosError<ApiError>(error)) return fallback;

  const detail = error.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (!Array.isArray(detail)) return fallback;

  const messages = detail.flatMap((issue) => {
    if (typeof issue.msg !== 'string') return [];
    const field = issue.loc
      ?.filter((part) => typeof part === 'string')
      .at(-1);
    return [field ? `${field}: ${issue.msg}` : issue.msg];
  });

  return messages.join('; ') || fallback;
}
