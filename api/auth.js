const { createClient } = require('@vercel/kv');

const kv = createClient({
  url: process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL || '',
  token: process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN || ''
});

module.exports = async function handler(req, res) {
  const { action, id, pass, name, bday } = req.body || req.query;

  if (!id) return res.status(400).json({ error: 'Missing id' });

  try {
    if (action === 'register') {
      const existing = await kv.hget('users', id);
      if (existing) {
        return res.status(409).json({ error: 'User already exists' });
      }
      await kv.hset('users', { [id]: pass });
      
      // Initialize basic user structure
      await kv.hset(`user_data:${id}`, {
        profile_name: name || '',
        profile_bday: bday || '',
        photos: [], events: [], memos: [], bookmarks: [], diaries: [], personal_news: []
      });
      return res.status(200).json({ success: true });
      
    } else if (action === 'login') {
      const actualPass = await kv.hget('users', id);
      if (actualPass !== null && actualPass === pass) {
        return res.status(200).json({ success: true });
      }
      return res.status(401).json({ error: 'Unauthorized' });
      
    } else if (action === 'admin_login') {
      const adminPass = await kv.hget('global_data', 'admin_pass');
      const passToCheck = adminPass || '1234';
      if (pass === passToCheck) {
        return res.status(200).json({ success: true });
      }
      return res.status(401).json({ error: 'Unauthorized' });
    }
    
    return res.status(400).json({ error: 'Invalid action' });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
};
