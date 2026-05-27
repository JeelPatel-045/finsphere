"use client";

import { useEffect, useState } from "react";

import API from "@/lib/api";

export default function UploadedDocuments() {
  const [documents, setDocuments] =
    useState([]);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    const response =
      await API.get("/documents");

    setDocuments(response.data);
  };

  return (
    <div className="space-y-4">
      {documents.map((doc: any) => (
        <div
          key={doc.id}
          className="bg-slate-900 p-4 rounded-xl"
        >
          <h3>{doc.name}</h3>

          <p>{doc.type}</p>
        </div>
      ))}
    </div>
  );
}