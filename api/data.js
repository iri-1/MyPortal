const { createClient } = require('@vercel/kv');

const kv = createClient({
  url: process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL || process.env.MY_KV_REST_API_URL || '',
  token: process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN || process.env.MY_KV_REST_API_TOKEN || ''
});

module.exports = async function handler(req, res) {
  const { action, group, key, val } = req.body || req.query;
  
  if (!group) return res.status(400).json({ error: 'Missing group' });

  try {
    if (action === 'get_all') {
      const data = await kv.hgetall(group);
      return res.status(200).json({ data: data || {} });
      
    } else if (action === 'get') {
      const data = await kv.hget(group, key);
      return res.status(200).json({ data });
      
    } else if (action === 'set') {
      let update = {};
      update[key] = val;
      await kv.hset(group, update);
      return res.status(200).json({ success: true });
      
    } else if (action === 'del') {
      await kv.hdel(group, key);
      return res.status(200).json({ success: true });
    }
    
    return res.status(400).json({ error: 'Invalid action' });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
};
