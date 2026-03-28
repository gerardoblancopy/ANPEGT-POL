import { clsx } from 'clsx';
import type { ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(n: number): string {
  return new Intl.NumberFormat('es-ES').format(n);
}

export function formatPercent(n: number): string {
  return `${(n * 100).toFixed(1)}%`;
}
