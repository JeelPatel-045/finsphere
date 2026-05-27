import API from "@/lib/api";

export const uploadDocument = async (
  file: File
) => {
  const formData = new FormData();

  formData.append("file", file);

  const response = await API.post(
    "/documents/upload",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    }
  );

  return response.data;
};