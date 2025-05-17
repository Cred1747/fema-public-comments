library(pdftools)

# Load the dataset
df <- read.csv("C:/Users/cred1/Desktop/Fema/DHS-2025-0013_batches/DHS-2025-0013_master_clean.csv", stringsAsFactors = FALSE)

# Set folder where actual PDF files are stored
pdf_folder <- "C:/Users/cred1/Desktop/Fema/DHS-2025-0013_batches/attachments"

# Add a column to hold the extracted PDF text
df$pdf_text <- NA

# Extract PDF text
for (i in 1:nrow(df)) {
  pdf_raw_path <- df$pdf_file_path[i]

  if (!is.na(pdf_raw_path) && pdf_raw_path != "") {
    # Extract just the file name, even if full or partial path is present
    file_name <- basename(pdf_raw_path)
    full_pdf_path <- file.path(pdf_folder, file_name)

    if (file.exists(full_pdf_path)) {
      text <- tryCatch({
        paste(pdf_text(full_pdf_path), collapse = "\n")
      }, error = function(e) NA)

      df$pdf_text[i] <- text
    }
  }
}

# Save result
write.csv(df, "C:/Users/cred1/Desktop/Fema/DHS-2025-0013_batches/DHS-2025-0013_master_with_pdf.csv", row.names = FALSE)
