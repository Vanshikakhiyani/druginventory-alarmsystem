document.getElementById('addDrugForm').addEventListener('submit', async (e) => {
  e.preventDefault(); // Prevent form submission

  const data = {
      Drug_Name: document.getElementById('drugName').value,
      Batch_Number: document.getElementById('batchNumber').value,
      Manufacture_Date: document.getElementById('manufactureDate').value,
      Expiry_Date: document.getElementById('expiryDate').value,
      Supplier_ID: document.getElementById('supplierId').value,
      Supplier_Name: document.getElementById('supplierName').value,
      Supply_Date: document.getElementById('supplyDate').value,
      Purchase_Order_ID: document.getElementById('purchaseOrderId').value,
      Quantity: parseInt(document.getElementById('quantity').value),
      Warehouse_ID: document.getElementById('warehouseId').value,
      Warehouse_Location: document.getElementById('warehouseLocation').value,
      Stock_In_Date: document.getElementById('stockInDate').value,
      Current_Stock_Level: parseInt(document.getElementById('currentStockLevel').value),
      Predicted_Expiry_Risk: document.getElementById('predictedExpiryRisk').value,
  };

  try {
      // Make a POST request to add the drug
      const response = await fetch('/add_drug', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
      });

      if (response.ok) {
          const result = await response.json();
          alert(result.message); // Show message from the backend
          loadDrugs(); // Reload the drug list
          document.getElementById('addDrugForm').reset(); // Clear the form
      } else {
          const error = await response.json();
          alert("Error: " + error.message);
      }
  } catch (error) {
      console.error('Error:', error);
      alert("An error occurred while adding the drug.");
  }
});

// Function to load the drug list
async function loadDrugs() {
  try {
      const response = await fetch('/drugs');
      const drugs = await response.json();
      const drugsList = document.getElementById('drugsList');
      drugsList.innerHTML = ''; // Clear the list before updating

      drugs.forEach(drug => {
          const li = document.createElement('li');
          li.textContent = `Name: ${drug.Drug_Name}, Batch: ${drug.Batch_Number}, Expiry: ${drug.Expiry_Date}`;
          drugsList.appendChild(li);
      });
  } catch (error) {
      console.error('Error fetching drugs:', error);
  }
}

// Load drugs on page load
window.onload = loadDrugs;
