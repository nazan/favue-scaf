/**
 * WebSocket channel names. Must match backend `app/topic_utils.py` conventions.
 */
export const PUBLIC_CHANNEL = 'public'

export function userChannel(userId) {
  return `user-${userId}`
}
