from cfpb.complaints import CFPBComplaintReader

reader = CFPBComplaintReader(
    companies=["BANK OF AMERICA, NATIONAL ASSOCIATION"],
    start_date_YYYY_MM_DD="2025-01-01",
    end_date_YYYY_MM_DD="2025-01-31",
    verbose=True,
)

documents = reader.load_data()

print(len(documents))
print(documents[0].text)
print(documents[0].metadata)