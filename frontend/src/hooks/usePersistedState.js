/**
 * React Hook that persists state to sessionStorage.
 * State survives page navigation (remount), cleared when tab closes.
 */
import { useState, useEffect, useCallback } from 'react';

const STORE = {};

function read(key, fallback) {
  try {
    if (STORE[key] !== undefined) return STORE[key];
    const raw = sessionStorage.getItem(key);
    if (raw !== null && raw !== undefined) {
      const val = JSON.parse(raw);
      STORE[key] = val;
      return val;
    }
  } catch (_) { /* ignore */ }
  return typeof fallback === 'function' ? fallback() : fallback;
}

function write(key, value) {
  STORE[key] = value;
  try { sessionStorage.setItem(key, JSON.stringify(value)); } catch (_) { /* quota */ }
}

function remove(key) {
  delete STORE[key];
  try { sessionStorage.removeItem(key); } catch (_) { /* ignore */ }
}

/**
 * Works exactly like useState(), but persists the value in sessionStorage
 * so it survives component unmount / remount during navigation.
 *
 * @param {string} key  unique storage key
 * @param {*}      initialValue
 */
export function usePersistedState(key, initialValue) {
  const [value, setValue] = useState(() => read(key, initialValue));

  useEffect(() => {
    write(key, value);
  }, [key, value]);

  const set = useCallback((v) => {
    setValue((prev) => {
      const next = typeof v === 'function' ? v(prev) : v;
      return next;
    });
  }, []);

  const clear = useCallback(() => {
    setValue(typeof initialValue === 'function' ? initialValue() : initialValue);
    remove(key);
  }, [key, initialValue]);

  return [value, set, clear];
}

export default usePersistedState;
