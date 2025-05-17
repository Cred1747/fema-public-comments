# Step 1: Read in the data
df <- read.csv("C:/Users/cred1/Desktop/Fema/DHS-2025-0013_batches/DHS-2025-0013_master.csv", stringsAsFactors = FALSE)

# Step 2: Create folder if it doesn't exist
dir.create("C:/Users/cred1/Desktop/Fema/DHS-2025-0013_batches", showWarnings = FALSE, recursive = TRUE)

# Step 3: Remove duplicates by comment_id (keep first)
df_clean <- df[!duplicated(df$comment_id), ]

# Step 4: Write cleaned CSV
write.csv(df_clean, "C:/Users/cred1/Desktop/Fema/DHS-2025-0013_batches/DHS-2025-0013_master_clean.csv", row.names = FALSE)
