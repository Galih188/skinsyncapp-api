const axios = require("axios");
const FormData = require("form-data");

// URL tempat layanan ML Python Anda berjalan
const ML_SERVICE_URL = "http://localhost:5000/predict";

exports.analyzeSkin = async (req, res) => {
  const { image } = req.body;
  if (!image) {
    return res.status(400).json({ error: "Image data is required." });
  }

  try {
    const base64Data = image.replace(/^data:image\/\w+;base64,/, "");
    const imageBuffer = Buffer.from(base64Data, "base64");

    const form = new FormData();
    form.append("file", imageBuffer, {
      filename: "upload.jpg",
      contentType: "image/jpeg",
    });

    // Memanggil API Python dengan metode POST
    const response = await axios.post(ML_SERVICE_URL, form, {
      headers: {
        ...form.getHeaders(),
      },
    });

    const pythonData = response.data;

    const frontendData = {
      skin_type: pythonData.skin_type,
      recommendations: pythonData.recommendation,
      description: `Hasil analisis menunjukkan jenis kulit Anda adalah ${pythonData.skin_type}.`,
    };
    // Kirim kembali hasil dari layanan ML ke klien
    res.status(200).json({ data: frontendData });
  } catch (error) {
    console.error("Error calling ML service:", error.message);
    res.status(500).json({ error: "Failed to analyze skin." });
  }
};
