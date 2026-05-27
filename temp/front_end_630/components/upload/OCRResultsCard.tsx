"use client";

import { useEffect, useState } from "react";

import API from "@/lib/api";

export default function OCRResultsCard() {
  const [ocr, setOCR] = useState(null);

  useEffect(() => {
    loadOCR();
  }, []);

  const loadOCR = async () => {
    const response =
      await API.get("/documents/ocr");

    setOCR(response.data);
  };

  if (!ocr) {
    return <div>Loading OCR...</div>;
  }

  return (
    <div className="space-y-4">
      <div>{ocr.vendor}</div>

      <div>{ocr.amount}</div>

      <div>{ocr.gst}</div>
    </div>
  );
}