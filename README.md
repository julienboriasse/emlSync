# emlSync

## Summary

This is a custom Python tool to upload emails from a local folder to a remote IMAP server.

## Situation

I used to manage my emails with ProtonMail (excellent service, by the way). For personal reasons, I decided to migrate to the Apple iCloud email service. 
ProtonMail provides an easy-to-use tool to retrieve and download all your emails locally. The operation took a few hours but worked great, and I now have several thousands of .eml files on my computer.
So, here is the Python script I developed to do the job!

## Few technical considerations

If you have a few thousand emails to migrate, a connection issue will probably happen while uploading. To mitigate this issue and to prevent duplicated emails, the script works in two phases:

1 - Scan: Scan the folders and record every email information as a new SQLite local database record

2 - Upload: For each unhandled record, try to upload the email and update its status (uploaded or failed) in the database. 
  
If remote server closes connection (or you disconnect your wifi...), the script will check for SQLite database existance. If the SQLite database is found it will ignore the Scan operation and directly resume the Upload operation.
If you want to force the Scan operation, simply manually delete the database file. Be careful, doing this might result in duplicate email upload.
