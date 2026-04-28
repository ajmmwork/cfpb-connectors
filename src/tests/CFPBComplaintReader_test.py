from cfpb.complaints import CFPBComplaintReader

reader = CFPBComplaintReader(
    ["BANK OF AMERICA, NATIONAL ASSOCIATION"],
    start_date_YYYY_MM_DD="2025-01-01",
    end_date_YYYY_MM_DD="2025-01-31"
)

docs = reader.load_data()
print(len(docs))
print(docs[0].text[:500])
print(docs[0].metadata)
