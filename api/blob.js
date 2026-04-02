const { put, del } = require('@vercel/blob');

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).send('Method Not Allowed');
  
  try {
    // Requires express-like body parser on Vercel which handles JSON out of the box
    const { action, filename, base64, url } = req.body;
    
    if (action === 'delete') {
      if (!url) return res.status(400).json({ error: 'Missing url' });
      await del(url, { token: process.env.BLOB_READ_WRITE_TOKEN });
      return res.status(200).json({ success: true });
    }
    
    if (!filename || !base64) return res.status(400).json({ error: 'Missing filename or base64' });

    // Expecting base64 to be e.g., "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
    const base64Data = base64.includes(',') ? base64.split(',')[1] : base64;
    const buffer = Buffer.from(base64Data, 'base64');
    
    const blob = await put(filename, buffer, {
      access: 'public',
      token: process.env.BLOB_READ_WRITE_TOKEN
    });
    
    return res.status(200).json({ url: blob.url });
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
};
